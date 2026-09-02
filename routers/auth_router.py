from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse # TAMBAH INI
from jose import JWTError, jwt
from sqlalchemy.orm import Session, joinedload
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
        email: str = payload.get("sub")
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
        password=hashed_password,
        role='showroom',
        status='pending'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_showroom

@router.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.showroom)).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    if user.status != 'approved':
        raise HTTPException(status_code=403, detail="Akun belum aktif. Hubungi admin")
    
    if user.role == 'showroom' and user.showroom.status != 'approved':
        raise HTTPException(status_code=403, detail="Showroom belum diapprove admin")
    
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    access_token = create_access_token(data={
        "sub": user.email, 
        "role": user.role, 
        "showroom_id": user.showroom_id
    })

    # KUNCI: NAMA COOKIE BEDA BERDASARKAN ROLE
    cookie_name = "admin_token" if user.role == "admin" else "showroom_token"

    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "showroom_id": user.showroom_id,
            "nama": user.name
        }
    })
    response.set_cookie(
        key=cookie_name,
        value=access_token,
        httponly=True,   # JS gak bisa baca. Aman
        samesite="lax",
        secure=False,    # kalau udah https di railway ganti True
        max_age=60*60*24*7 # 7 hari
    )
    return response

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
            status="approved",
            showroom_id=None
        )
        db.add(user)
    else:
        user.password = new_hash
        user.role = "admin"
        user.status = "approved"
    
    db.commit()
    return {"msg": "Admin reset berhasil. Password: admin123"}

@router.post("/reset-showroom/{id}")
def reset_showroom_password(id: int, db: Session = Depends(get_db)):
    new_hash = hash_password("123456")
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    user.password = new_hash
    user.status = "approved"
    db.commit()
    return {"msg": f"Password user {user.email} direset ke 123456"}
