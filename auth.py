from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas  # <-- UDAH DIHAPUS "app."
from database import get_db  # <-- UDAH DIHAPUS "app."

router = APIRouter(prefix="/auth", tags=["Auth"])

# Mesin buat ngacak password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Dipake pas register. Ubah '123456' jadi '$2b$12$...' """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Dipake pas login. Ngecek '123456' == '$2b$12$...' """
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register", response_model=schemas.ShowroomResponse)
def register_showroom(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db)):
    # 1. Cek subdomain udah ada belum
    db_showroom = db.query(models.Showroom).filter(models.Showroom.subdomain == showroom.subdomain).first()
    if db_showroom:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")

    # 2. Cek email udah ada belum
    db_user = db.query(models.UserShowroom).filter(models.UserShowroom.email == showroom.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # 3. Hash password
    hashed_password = hash_password(showroom.password)

    # 4. Buat Showroom baru
    new_showroom = models.Showroom(
        nama_showroom=showroom.nama_showroom,
        subdomain=showroom.subdomain,
        wa_number=showroom.wa_number,
        alamat=showroom.alamat,
        deskripsi=showroom.deskripsi,
        logo=showroom.logo
    )
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)

    # 5. Buat User Showroom
    new_user = models.UserShowroom(
        showroom_id=new_showroom.id,
        email=showroom.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()

    return new_showroom

@router.post("/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.UserShowroom).filter(models.UserShowroom.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    showroom = db.query(models.Showroom).filter(models.Showroom.id == user.showroom_id).first()
    return {
        "message": "Login Berhasil", 
        "showroom": showroom
    }
