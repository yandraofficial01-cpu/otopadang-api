from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # TAMBAH INI
from jose import JWTError, jwt # TAMBAH INI
from sqlalchemy.orm import Session
from database import get_db
from models import UserShowroom, Showroom
import bcrypt
from dependencies import create_access_token
import schemas
import os # TAMBAH INI

router = APIRouter(prefix="/auth", tags=["Auth Showroom"])

ADMIN_EMAILS = ["admin@otopadang.com", "yandraofficial01@gmail.com"] 
WA_ADMIN = "628979879518"

# 1. TAMBAHIN 3 BARIS INI - WAJIB BUAT ADMIN
SECRET_KEY = os.getenv("SECRET_KEY", "rahasia-super-penting-ganti-di-railway") 
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# 2. TAMBAHIN FUNCTION INI PALING BAWAH - INI YG DICARI ADMIN_ROUTER
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tidak bisa validasi token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email") # lu bikin token pake "email"
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserShowroom).filter(UserShowroom.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=schemas.ShowroomResponse)
def register_showroom(showroom: schemas.RegisterShowroomRequest, db: Session = Depends(get_db)):
    ... # kode lu yg lama biarin

@router.post("/login")
def login_showroom(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    ... # kode lu yg lama biarin
