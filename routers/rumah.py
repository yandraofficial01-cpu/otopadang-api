from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Rumah
import schemas # <-- tambahin ini biar pake response_model

router = APIRouter() # <-- PREFIX DIHAPUS. Nanti diset di main.py

# 1. PUBLIC LIHAT SEMUA RUMAH YANG AVAILABLE
@router.get("/all-public", response_model=list[schemas.RumahResponse]) # <-- pake schema
def get_all_rumah_public(db: Session = Depends(get_db)):
    rumah_list = db.query(Rumah).filter(Rumah.status == "available").order_by(Rumah.id.desc()).all()
    return rumah_list # <-- langsung return model. FastAPI yg convert ke json

# 2. PUBLIC LIHAT DETAIL 1 RUMAH - TAMBAHIN BIAR LENGKAP
@router.get("/{rumah_id}", response_model=schemas.RumahResponse)
def get_rumah_detail(rumah_id: int, db: Session = Depends(get_db)):
    rumah = db.query(Rumah).filter(
        Rumah.id == rumah_id,
        Rumah.status == "available"
    ).first()
    if not rumah:
        raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    return rumah


Jadi apa bener ini kodenya?
