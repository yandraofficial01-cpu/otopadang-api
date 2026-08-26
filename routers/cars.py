from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter() # <-- PREFIX KOSONG. Nanti diset di main.py jadi /cars

# 1. PUBLIC LIHAT MOBIL YANG SUDAH APPROVED
@router.get("/all-public", response_model=list[schemas.MobilResponse])
def get_cars_public(db: Session = Depends(get_db)):
    cars = db.query(models.Car).filter(models.Car.status == "approved").all()
    return cars

# 2. PUBLIC LIHAT DETAIL 1 MOBIL
@router.get("/{mobil_id}", response_model=schemas.MobilResponse)
def get_car_detail(mobil_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(
        models.Car.id == mobil_id, 
        models.Car.status == "approved"
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    return car
