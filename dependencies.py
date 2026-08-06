from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # GANTI DARI Oauth2
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from models import UserShowroom
import os

# 1. AMBIL DARI ENV BIAR AMAN DI RAILWAY
SECRET_KEY = os.getenv("SECRET_KEY", "otopadang-super-secret-key-2026-ganti-yg-random-32-karakter")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 hari

security = HTTPBearer() # INI YG DIGANTI

def create_access_token(data: dict):
    """Buat token pas login"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)): # GANTI PARAMETER
    """Satpam 1: Cek token valid apa enggak. Return OBJECT UserShowroom"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials # AMBIL TOKEN DARI SINI
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id") # INI YG KITA KIRIM DARI auth_router
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # AMBIL DATA USER DARI DB BIAR BISA AKSES .email .role
    user = db.query(UserShowroom).filter(UserShowroom.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user # <--- INI KUNCI NYA. RETURN OBJECT

def require_admin(current_user: UserShowroom = Depends(get_current_user)):
    """Satpam 2: Cek harus admin. Dipake buat menu khusus admin"""
    ADMIN_EMAILS = ["admin@otopadang.com", "yandraofficial01@gmail.com"] # TARUH DI SINI JUGA BIAR AMAN
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Khusus Admin Pusat"
        )
    return current_user
