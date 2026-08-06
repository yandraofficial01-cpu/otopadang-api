from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import UserShowroom, Showroom
import bcrypt
from dependencies import create_access_token
import schemas

router = APIRouter(prefix="/auth", tags=["Auth Showroom"])

# WAJIB ADA INI BIAR showroom.py GA ERROR
ADMIN_EMAILS = ["admin@otopadang.com", "yandraofficial01@gmail.com"] 
WA_ADMIN = "628979879518"

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/register", response_model=schemas.ShowroomResponse)
def register_showroom(showroom: schemas.RegisterShowroomRequest, db: Session = Depends(get_db)):
    """Buat showroom daftar dari public. Status pending"""
    db_showroom = db.query(Showroom).filter(Showroom.subdomain == showroom.subdomain).first()
    if db_showroom:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")

    db_user = db.query(UserShowroom).filter(UserShowroom.email == showroom.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    hashed_password = hash_password(showroom.password)

    new_showroom = Showroom(
        nama_showroom=showroom.nama_showroom,
        subdomain=showroom.subdomain,
        wa_number=showroom.wa_number,
        alamat=showroom.alamat,
        status="pending",
        status_bayar="expired", 
        status_akun="nonaktif",
        paket="Basic"
    )
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)

    new_user = UserShowroom(
        showroom_id=new_showroom.id,
        email=showroom.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    return new_showroom

@router.post("/login")
def login_showroom(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login buat admin dan showroom"""
    user = db.query(UserShowroom).filter(UserShowroom.email == request.email).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Email atau password salah")

    showroom = db.query(Showroom).filter(Showroom.id == user.showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    if showroom.status != "approved":
        raise HTTPException(status_code=403, detail="Akun showroom belum di approve admin")
    
    if showroom.status_bayar != "aktif":
        raise HTTPException(status_code=403, detail="Paket showroom sudah expired")

    role = "admin" if user.email in ADMIN_EMAILS else "showroom"

    access_token = create_access_token(
        data={"sub": user.email, "role": role, "showroom_id": showroom.id}
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": role,
        "showroom": showroom
    }
