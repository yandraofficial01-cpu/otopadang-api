from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas 
from database import get_db
from .admin_auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin Rumah"])

@router.get("/rumah", response_model=list[schemas.RumahResponse])
def get_all_rumah_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.House).order_by(models.House.id.desc()).all()

@router.post("/rumah", response_model=schemas.RumahResponse)
@router.post("/upload-rumah", response_model=schemas.RumahResponse)
def upload_rumah(data: schemas.RumahCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    new_rumah = models.House(**data.model_dump()); db.add(new_rumah); db.commit(); db.refresh(new_rumah); return new_rumah

@router.put("/rumah/{rumah_id}")
def update_rumah_status(rumah_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    rumah = db.query(models.House).filter(models.House.id == rumah_id).first()
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    for key, value in data.items(): setattr(rumah, key, value)
    db.commit(); return {"message": f"Status rumah diupdate"}

@router.delete("/rumah/{rumah_id}")
def delete_rumah(rumah_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    rumah = db.query(models.House).filter(models.House.id == rumah_id).first()
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    db.delete(rumah); db.commit(); return {"message": "Rumah dihapus"}
