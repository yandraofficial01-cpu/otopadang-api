from fastapi import APIRouter, Depends, HTTPException, status, Request # TAMBAH Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import User, Showroom
import bcrypt
from dependencies import create_access_token
import schemas
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "rahasia-super-penting-ganti-di-vercel")
ALGORITHM = "HS256"

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# UBAH INI: BISA BACA DARI COOKIE DAN HEADER
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("admin_token") or request.cookies.get("showroom_token")

    # fallback kalau pake header
    if not token:
        auth: str = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401, detail="Tidak bisa validasi token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Tidak bisa validasi token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Tidak bisa validasi token")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Tidak bisa validasi token")
    return user

@router.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.showroom)).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email atau password salah")

    if user.status!= 'approved':
        raise HTTPException(status_code=403, detail="Akun belum aktif. Hubungi admin")

    if user.role == 'showroom' and user.showroom and user.showroom.status!= 'approved':
        raise HTTPException(status_code=403, detail="Showroom belum diapprove admin")

    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Email atau password salah")

    access_token = create_access_token(data={
        "sub": user.email,
        "role": user.role,
        "showroom_id": user.showroom_id
    })

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
        httponly=True,
        samesite="None", # GANTI JADI N GEDE
        secure=True, # WAJIB TRUE
        max_age=60*60*24*7, # 7 hari
        path="/"
    )
    return response

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "status": "ok"
    }
