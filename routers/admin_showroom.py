from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routers.admin_auth import require_admin  # <-- GANTI TITIK JADI routers
from database import get_db
from models import Showroom

router = APIRouter(prefix="/admin/showroom", tags=["Admin Showroom"]) # <-- TAMBAH PREFIX

@router.get("/")
def get_all_showroom(db: Session = Depends(get_db), admin = Depends(require_admin)):
    # Sementara ambil semua dulu. Nanti kalau kolom status udah ada baru pakai filter
    showrooms = db.query(Showroom).all()
    return showrooms

@router.put("/{showroom_id}/approve")
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    # Kalau kolom status belum ada di model, comment dulu baris ini
    # showroom.status = "approved"
    
    db.commit()
    db.refresh(showroom)
    return {"message": f"Showroom {showroom.nama_showroom} berhasil di approve", "data": showroom}

@router.put("/{showroom_id}/premium")
def set_premium(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    showroom.paket = "Premium"
    db.commit()
    db.refresh(showroom)
    return {"message": f"Showroom {showroom.nama_showroom} sudah Premium", "data": showroom}

@router.delete("/{showroom_id}")
def delete_showroom(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    db.delete(showroom)
    db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} berhasil dihapus"}
