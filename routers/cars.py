from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas 
from database import get_db
from .auth_router import get_current_user # PAKAI INI BUKAN ADMIN

router = APIRouter(prefix="/cars", tags=["Cars Showroom"])

@router.post("/")
def create_car(car_data: schemas.MobilCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "showroom":
        raise HTTPException(status_code=403, detail="Cuma showroom")
    return {"msg": "Showroom nambah mobil baru"}

@router.put("/{mobil_id}")
def update_car(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "showroom":
        raise HTTPException(status_code=403, detail="Cuma showroom")
    return {"msg": f"Showroom edit harga/spesifikasi mobil {mobil_id}"}
