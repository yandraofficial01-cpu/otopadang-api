from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import User, Showroom
import bcrypt
from dependencies import create_access_token # ini dari file lain
import schemas
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "rahasia-super-penting-ganti-di-vercel")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 hari

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tidak bisa validasi token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Cek dari Cookie dulu
    token = request.cookies.get("admin_token") or request.cookies.get("showroom_token")

    # 2. Fallback ke Header Bearer kalau ada
    if not token:
        auth: str = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") # PENTING: harus "sub" sama kayak pas create
        role: str = payload.get("role")
        if email is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).options(joinedload(User.showroom)).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role!= "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak. Khusus Admin")
    return current_user

def require_showroom(current_user: User = Depends(get_current_user)):
    if current_user.role!= "showroom":
        raise HTTPException(status_code=403, detail="Akses ditolak. Khusus Showroom")
    return current_user

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
        HTTPException(status_code=400, detail="Email atau password salah")

    # PENTING: payload harus ada "sub" biar get_current_user kebaca
    access_token = create_access_token(data={
        "sub": user.email, # <-- INI KUNCINYA
        "role": user.role,
        "showroom_id": user.showroom_id,
        "user_id": user.id
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
        samesite="none", # Wajib none untuk cross-site Vercel
        secure=True, # Wajib true karena https
        max_age=60*60*24*7,
        path="/"
        # domain dihapus biar otomatis ngikut domain BE. UDAH BENER
    )
    return response

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "nama": current_user.name,
        "showroom_id": current_user.showroom_id,
        "status": "ok"
    }

@router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(key="admin_token", path="/", samesite="none", secure=True)
    response.delete_cookie(key="showroom_token", path="/", samesite="none", secure=True)
    return response
