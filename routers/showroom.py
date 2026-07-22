from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date, datetime

from database import get_db
from models import Showroom, Car

router = APIRouter(tags=["Showroom"])

# 1. Schema buat POST daftar showroom
class ShowroomCreate(BaseModel):
    nama_showroom: str
    subdomain: str
    logo: str | None = None
    wa_number: str
    paket: str = "Basic"
    status_bayar: str = "aktif"
    tgl_expired: date | None = None

class ShowroomSchema(ShowroomCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# 2. ENDPOINT BUAT DAFTAR - INI YG KURANG
@router.post("/", response_model=ShowroomSchema)
def create_showroom(showroom: ShowroomCreate, db: Session = Depends(get_db)):
    # Cek subdomain biar gak double
    cek = db.query(Showroom).filter(Showroom.subdomain == showroom.subdomain).first()
    if cek:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")
    
    new_showroom = Showroom(**showroom.dict())
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)
    return new_showroom

# 3. KODE LU YG LAMA - BUAT LIAT HALAMAN PUBLIK
@router.get("/{subdomain}")
def get_public_showroom(subdomain: str, db: Session = Depends(get_db)):
    showroom = db.query(Showroom).filter(Showroom.subdomain == subdomain).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    cars = db.query(Car).filter(Car.showroom_id == showroom.id, Car.status == 'approved').all()
    
    return {
        "id": showroom.id,
        "nama_showroom": showroom.nama_showroom,
        "wa_number": showroom.wa_number,
        "logo": showroom.logo,
        "paket": showroom.paket,
        "cars": cars
    }
