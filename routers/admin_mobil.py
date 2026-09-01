from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from database import get_db
from routers.admin_auth import require_admin

router = APIRouter(prefix="/admin/mobil", tags=["Admin Mobil"]) # <--- PASTIIN PREFIX ADA DI SINI

def _to_dict(car, showroom_nama):
    mobil_dict = schemas.MobilResponse.model_validate(car).model_dump()
    mobil_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
    return mobil_dict

@router.get("/", response_model=list[dict])
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # Ambil semua mobil kecuali yang sudah SOLD biar ringan
    results = db.query(models.Car, models.Showroom.nama_showroom.label("showroom_nama")) \
       .outerjoin(models.Showroom, models.Car.showroom_id == models.Showroom.id) \
       .filter(models.Car.status_jual!= 'sold') \
       .order_by(models.Car.id.desc()).all()

    return [_to_dict(car, showroom_nama) for car, showroom_nama in results]

@router.get("/pending", response_model=list[dict])
def get_mobil_pending_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # FIX: pake status_jual bukan status
    results = db.query(models.Car, models.Showroom.nama_showroom.label("showroom_nama")) \
       .outerjoin(models.Showroom, models.Car.showroom_id == models.Showroom.id) \
       .filter(models.Car.status_jual == 'pending').order_by(models.Car.id.desc()).all()

    return [_to_dict(car, showroom_nama) for car, showroom_nama in results]

@router.put("/{mobil_id}/approve")
def approve_mobil(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    mobil.status = "approved" # buat admin
    mobil.status_jual = "tersedia" # buat tampil di web induk
    db.commit()
    db.refresh(mobil)
    return {"message": f"Mobil {mobil.nama_mobil} berhasil di-approve", "data": _to_dict(mobil, None)}

@router.put("/{mobil_id}/sold")
def sold_mobil(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    mobil.status = "sold"
    mobil.status_jual = "sold" # hilang dari web induk
    mobil.sold_at = func.now()
    db.commit()
    db.refresh(mobil)
    return {"message": f"Mobil {mobil.nama_mobil} ditandai Sold Out", "data": _to_dict(mobil, None)}

@router.put("/{mobil_id}")
def update_mobil_status(mobil_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    allowed = ["status", "status_jual", "harga", "deskripsi", "nama_mobil", "merek"]
    for key, value in data.items():
        if key in allowed:
            setattr(mobil, key, value)

    db.commit()
    db.refresh(mobil)
    return {"message": f"Status mobil {mobil_id} diupdate", "data": _to_dict(mobil, None)}

@router.delete("/{mobil_id}")
def delete_mobil(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    db.delete(mobil)
    db.commit()
    return {"message": "Mobil dihapus"}
