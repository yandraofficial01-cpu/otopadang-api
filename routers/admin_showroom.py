from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .admin_auth import require_admin
from database import get_db
from models import Showroom  # sesuaikan nama model lu

router = APIRouter(tags=["Admin Showroom"]) # HAPUS PREFIX DISINI

@router.get("/")
def get_all_showroom(db: Session = Depends(get_db), admin = Depends(require_admin)):
    # Tambah filter biar cuma yg approved yg muncul di FE
    showrooms = db.query(Showroom).filter(Showroom.status == 'approved').all()
    return showrooms

@router.put("/{showroom_id}/approve")
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    showroom.status = "approved"
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
