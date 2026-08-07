from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Showroom, User, Car  # UDAH GANTI INI
import schemas 
from routers.auth_router import ADMIN_EMAILS # Cuma ambil ADMIN_EMAILS dari sini
from dependencies import get_current_user, require_admin # AMBIL DARI SINI

router = APIRouter(prefix="/showroom", tags=["Showroom"])

# PALANG PINTU BUAT HALAMAN PUBLIK
def get_active_showroom(subdomain: str, db: Session = Depends(get_db)):
    showroom = db.query(Showroom).filter(Showroom.subdomain == subdomain).first()
    if not showroom: raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    if showroom.status != "approved": raise HTTPException(status_code=403, detail="Showroom belum di approve admin")
    if showroom.status_bayar == "expired":
        raise HTTPException(status_code=403, detail="Akun showroom ini sedang disuspend")
    return showroom

# 1. ENDPOINT BUAT ADMIN DAFTARIN MANUAL - UDAH DIKUNCI
@router.post("/", response_model=schemas.ShowroomResponse)
def create_showroom(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db), admin = Depends(require_admin)):
    cek = db.query(Showroom).filter(Showroom.subdomain == showroom.subdomain).first()
    if cek: raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")
    
    new_showroom = Showroom(**showroom.model_dump()) # .dict() udah deprecated di pydantic v2, ganti .model_dump()
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)
    return new_showroom

# 2. ENDPOINT BUAT ADMIN APPROVE
@router.put("/{id}/approve", response_model=schemas.ShowroomResponse)
def approve_showroom(id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == id).first()
    if not showroom: raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.status = "approved"
    db.commit()
    db.refresh(showroom)
    return showroom

# 3. KODE HALAMAN PUBLIK
@router.get("/{subdomain}")
def get_public_showroom(showroom = Depends(get_active_showroom), db: Session = Depends(get_db)):
    cars = db.query(Car).filter(Car.showroom_id == showroom.id, Car.status == 'approved').all()
    return {**schemas.ShowroomResponse.from_orm(showroom).dict(), "cars": cars}
