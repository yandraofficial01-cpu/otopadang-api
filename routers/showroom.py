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
    status_bayar: str = "aktif" # <--- ini buat kontrol suspend
    tgl_expired: date | None = None
    status: str = "approved" # <--- ini buat kontrol approval

class ShowroomSchema(ShowroomCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# FUNCTION PALANG PINTU
def get_active_showroom(subdomain: str, db: Session = Depends(get_db)):
    showroom = db.query(Showroom).filter(Showroom.subdomain == subdomain).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    # CEK 1: UDAH APPROVE BELUM
    if showroom.status != "approved":
        raise HTTPException(status_code=403, detail="Showroom belum di approve admin")
    
    # CEK 2: INI KUNCINYA - CEK BILLING
    if showroom.status_bayar == "belum_bayar": # <--- UDAH DIUBAH
        raise HTTPException(status_code=403, detail="Akun showroom ini sedang disuspend karena belum bayar")
    
    return showroom

# 2. ENDPOINT BUAT DAFTAR
@router.post("/", response_model=ShowroomSchema)
def create_showroom(showroom: ShowroomCreate, db: Session = Depends(get_db)):
    # Cek subdomain biar gak double
    cek = db.query(Showroom).filter(Showroom.subdomain == showroom.subdomain).first()
    if cek:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")
    
    new_showroom = Showroom(**showroom.dict())
    # pastiin default
    if new_showroom.status != "approved":
        new_showroom.status = "pending" # daftar public = pending dulu
    if not new_showroom.status_bayar:
        new_showroom.status_bayar = "aktif"
        
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)
    return new_showroom

# 3. KODE HALAMAN PUBLIK - UDAH DIKASIH PALANG
@router.get("/{subdomain}")
def get_public_showroom(showroom = Depends(get_active_showroom), db: Session = Depends(get_db)):
    # kalau lolos Depends berarti status = approved DAN status_bayar = aktif
    
    cars = db.query(Car).filter(Car.showroom_id == showroom.id, Car.status == 'approved').all()
    
    return {
        "id": showroom.id,
        "nama_showroom": showroom.nama_showroom,
        "wa_number": showroom.wa_number,
        "logo": showroom.logo,
        "paket": showroom.paket,
        "status_bayar": showroom.status_bayar,
        "status": showroom.status,
        "cars": cars
    }
