from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import User, Showroom  # UDAH BENER
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
    if hashed_password.startswith("$2b$"):
        hashed_password = hashed_password.replace("$2b$", "$2a$")
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tidak bisa validasi token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=schemas.ShowroomResponse)
def register_showroom(showroom: schemas.RegisterShowroomRequest, db: Session = Depends(get_db)):
    # 1. CEK EMAIL UDAH ADA BELUM
    existing_user = db.query(User).filter(User.email == showroom.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # 2. BUAT SHOWROOM DULU
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

    # 3. HASH PASSWORD
    hashed_password = hash_password(showroom.password)

    # 4. BUAT USER BARU - HAPUS name & phone
    new_user = User(
        showroom_id=new_showroom.id, # DIISI ID SHOWROOM
        email=showroom.email,
        password=hashed_password,
        role='showroom',
        status='pending' # ngikutin default DB lu
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Register berhasil", "showroom": new_showroom, "user": new_user}

@router.post("/login")
def login_showroom(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    if user.status != 'pending' and user.status != 'active': # biar pending juga bisa login
        raise HTTPException(status_code=400, detail="Akun belum aktif")

    access_token = create_access_token(data={"email": user.email, "role": user.role})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            # "name": user.name,  <-- HAPUS INI
            "role": user.role,
            "showroom_id": user.showroom_id
        }
    }
