from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import User, Showroom
import bcrypt
from dependencies import create_access_token
import schemas
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "rahasia-super-penting-ganti-di-railway") 
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tidak bisa validasi token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # PENTING: pake "sub" bukan "email"
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=schemas.ShowroomResponse, status_code=status.HTTP_201_CREATED)
def register_showroom(showroom: schemas.RegisterShowroomRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == showroom.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    existing_subdomain = db.query(Showroom).filter(Showroom.subdomain == showroom.subdomain).first()
    if existing_subdomain:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")

    new_showroom = Showroom(
        nama_showroom=showroom.nama_showroom,
        subdomain=showroom.subdomain,
        alamat=showroom.alamat,
        wa_number=showroom.wa_number,
        status='pending'
    )
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)

    hashed_password = hash_password(showroom.password)
    new_user = User(
        showroom_id=new_showroom.id,
        name=showroom.nama_showroom,
        email=showroom.email,
        phone=showroom.wa_number,
        password=hashed_password, # pastikan di models.py kolomnya 'password'
        role='showroom',
        status='active'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_showroom

@router.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    # 1. CEK STATUS
    if user.status != 'active':
        raise HTTPException(status_code=403, detail="Akun belum aktif. Hubungi admin")
    
    # 2. CEK PASSWORD
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    # 3. BIKIN TOKEN - KUNCI DI "sub"
    access_token = create_access_token(data={
        "sub": user.email, 
        "role": user.role, 
        "showroom_id": user.showroom_id
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "showroom_id": user.showroom_id,
            "nama": user.name
        }
    }

# UTILITY BUAT RESET
@router.post("/reset-admin")
def reset_admin(db: Session = Depends(get_db)):
    new_hash = hash_password("admin123")
    user = db.query(User).filter(User.email == "admin@otopadang.com").first()
    if not user:
        user = User(
            name="Admin Otopadang",
            email="admin@otopadang.com",
            phone="08979879518",
            password=new_hash,
            role="admin",
            status="active",
            showroom_id=None
        )
        db.add(user)
    else:
        user.password = new_hash
        user.role = "admin"
        user.status = "active"
    
    db.commit()
    return {"msg": "Admin reset berhasil. Password: admin123"}

@router.post("/reset-showroom/{id}")
def reset_showroom_password(id: int, db: Session = Depends(get_db)):
    new_hash = hash_password("123456")
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    user.password = new_hash
    user.status = "active"
    db.commit()
    return {"msg": f"Password user {user.email} direset ke 123456"}
