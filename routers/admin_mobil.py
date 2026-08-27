from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from routers.admin_auth import require_admin

router = APIRouter(prefix="/admin/mobil", tags=["Admin Mobil"])

def _to_dict(car, showroom_nama):
    mobil_dict = schemas.MobilResponse.model_validate(car).model_dump()
    mobil_dict['showroom_nama'] = showroom_nama or "Admin Pusat" # nambahin manual
    return mobil_dict

@router.get("/", response_model=list[dict]) # <-- ganti ke list[dict] biar bisa ada showroom_nama
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    results = db.query(models.Car, models.Showroom.nama_showroom.label("showroom_nama")) \
      .outerjoin(models.Showroom, models.Car.showroom_id == models.Showroom.id) \
      .order_by(models.Car.id.desc()).all()
    
    return [_to_dict(car, showroom_nama) for car, showroom_nama in results]

@router.get("/pending", response_model=list[dict]) # <-- ganti ke list[dict]
def get_mobil_pending_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    results = db.query(models.Car, models.Showroom.nama_showroom.label("showroom_nama")) \
      .outerjoin(models.Showroom, models.Car.showroom_id == models.Showroom.id) \
      .filter(models.Car.status == 'pending').order_by(models.Car.id.desc()).all()
    
    return [_to_dict(car, showroom_nama) for car, showroom_nama in results]

@router.put("/{mobil_id}")
def update_mobil_status(mobil_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    # yg boleh diupdate admin
    allowed = ["status", "harga", "deskripsi"] 
    for key, value in data.items():
        if key in allowed:
            setattr(mobil, key, value)
            
    db.commit()
    db.refresh(mobil)
    return {"message": f"Status mobil {mobil_id} diupdate jadi {mobil.status}", "data": _to_dict(mobil, None)}

@router.delete("/{mobil_id}")
def delete_mobil(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    db.delete(mobil)
    db.commit()
    return {"message": "Mobil dihapus"}
