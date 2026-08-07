from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from models import User  # UDAH GANTI INI
import os

# 1. AMBIL DARI ENV BIAR AMAN DI RAILWAY
SECRET_KEY = os.getenv("SECRET_KEY", "otopadang-super-secret-key-2026-ganti-yg-random-32-karakter")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 hari

security = HTTPBearer()

def create_access_token(data: dict):
    """Buat token pas login"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Satpam 1: Cek token valid apa enggak. Return OBJECT User"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email") # GANTI JADI EMAIL BIAR SAMA KAYAK auth.py
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # AMBIL DATA USER DARI DB BIAR BISA AKSES .email .role
    user = db.query(User).filter(User.email == email).first() # UDAH GANTI INI
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user: User = Depends(get_current_user)): # UDAH GANTI INI
    """Satpam 2: Cek harus admin. Dipake buat menu khusus admin"""
    ADMIN_EMAILS = ["admin@otopadang.com", "yandraofficial01@gmail.com"]
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Khusus Admin Pusat"
        )
    return current_user
