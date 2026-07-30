from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta

# 1. CONFIG JWT - GANTI YG PANJANG YA BRO
SECRET_KEY = "otopadang-super-secret-key-2026-ganti-yg-random-32-karakter"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 hari

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict):
    """Buat token pas login"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Satpam 1: Cek token valid apa enggak. Dipake di semua API yg login"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        showroom_id: int = payload.get("showroom_id")
        
        if user_id is None or role is None:
            raise credentials_exception
            
        # Balikin data user dari token
        return {"user_id": user_id, "role": role, "showroom_id": showroom_id}
        
    except JWTError:
        raise credentials_exception

def require_admin(current_user: dict = Depends(get_current_user)):
    """Satpam 2: Cek harus admin. Dipake buat menu khusus admin"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Khusus Admin Pusat"
        )
    return current_user
