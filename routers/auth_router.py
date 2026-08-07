from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import UserShowroom, Showroom
import bcrypt
from dependencies import create_access_token
import schemas
import os

router = APIRouter(prefix="/auth", tags=["Auth Showroom"])

ADMIN_EMAILS = ["admin@otopadang.com", "yandraofficial01@gmail.com"] 
WA_ADMIN = "628979879518"

SECRET_KEY = os.getenv("SECRET_KEY", "rahasia-super-penting-ganti-di-railway") 
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str):
    # FIX PENTING BUAT TiDB: bcrypt python gak support $2b$
    # Jadi kita ganti ke $2a$ dulu sebelum verify
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
    
    user = db.query(UserShowroom).filter(UserShowroom.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=schemas.ShowroomResponse)
def register_showroom(showroom: schemas.RegisterShowroomRequest, db: Session = Depends(get_db)):
    # CEK EMAIL UDAH ADA BELUM
    existing_user = db.query(UserShowroom).filter(UserShowroom.email == showroom.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # HASH PASSWORD
    hashed_password = hash_password(showroom.password)

    # BUAT USER BARU - DEFAULT ROLE SHOWROOM
    new_user = UserShowroom(
        name=showroom.name,
        email=showroom.email,
        password=hashed_password,
        phone=showroom.phone,
        role='showroom',  # default showroom
        status='active', # <-- TAMBAHIN INI BIAR LANGSUNG AKTIF
        showroom_id=None  # nanti diisi pas approve
    )
    db.add(new_user)

    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login_showroom(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. CARI USER DARI EMAIL
    user = db.query(UserShowroom).filter(
        UserShowroom.email == request.email
    ).first()

    # 2. CEK USER ADA GAK + PASSWORD BENER GAK
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email atau password salah"
        )
    
    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email atau password salah"
        )
    
    # 3. CEK STATUS AKTIF
    if user.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Akun belum aktif"
        )

    # 4. BUAT TOKEN + KIRIM ROLE JUGA
    access_token = create_access_token(data={
        "email": user.email,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "showroom_id": user.showroom_id
        }
    }
