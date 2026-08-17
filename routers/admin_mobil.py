from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from.admin_auth import require_admin

router = APIRouter(prefix="/admin/mobil", tags=["Admin Mobil"])

@router.get("/", response_model=list[schemas.MobilResponse])
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    results = db.query(models.Car, models.Showroom.nama_showroom.label("showroom_nama")) \
       .outerjoin(models.Showroom, models.Car.showroom_id == models.Showroom.id) \
       .order_by(models.Car.id.desc()).all()
    mobil_list = []
    for car, showroom_nama in results:
        mobil_dict = schemas.MobilResponse.model_validate(car).model_dump()
        mobil_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
        mobil_list.append(mobil_dict)
    return mobil_list

@router.get("/pending", response_model=list[schemas.MobilResponse])
def get_mobil_pending_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    results = db.query(models.Car, models.Showroom.nama_showroom.label("showroom_nama")) \
       .outerjoin(models.Showroom, models.Car.showroom_id == models.Showroom.id) \
       .filter(models.Car.status == 'pending').order_by(models.Car.id.desc()).all()
    mobil_list = []
    for car, showroom_nama in results:
        mobil_dict = schemas.MobilResponse.model_validate(car).model_dump()
        mobil_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
        mobil_list.append(mobil_dict)
    return mobil_list

@router.put("/{mobil_id}")
def update_mobil_status(mobil_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    for key, value in data.items(): setattr(mobil, key, value)
    db.commit(); db.refresh(mobil)
    return {"message": f"Status mobil {mobil_id} diupdate", "data": mobil}

@router.delete("/{mobil_id}")
def delete_mobil(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    db.delete(mobil); db.commit(); return {"message": "Mobil dihapus"}
