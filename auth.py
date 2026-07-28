from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas 
from database import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register-showroom", response_model=schemas.ShowroomResponse)
def register_showroom(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db)):
    # 1. Cek subdomain
    db_showroom = db.query(models.Showroom).filter(models.Showroom.subdomain == showroom.subdomain).first()
    if db_showroom:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")

    # 2. Cek email
    db_user = db.query(models.UserShowroom).filter(models.UserShowroom.email == showroom.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # 3. Hash password
    hashed_password = hash_password(showroom.password)

    # 4. Buat Showroom
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

@router.post("/upload-rumah") # <-- NANTI TARUH DISINI ENDPOINT UPLOAD RUMAH
def upload_rumah():
    return {"msg": "Endpoint upload rumah. Nanti kita isi"}
