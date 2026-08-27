from fastapi import APIRouter, Depends, HTTPException # <-- INI WAJIB
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter()

@router.get("/all-public", response_model=list[schemas.MobilResponse])
def get_cars_public(db: Session = Depends(get_db)):
    cars = db.query(models.Car).filter(models.Car.status == "approved").order_by(models.Car.id.desc()).all()
    
    result = []
    for car in cars:
        data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
        showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first() if car.showroom_id else None
        data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"
        result.append(schemas.MobilResponse(**data)) # <-- PENTING: CAST KE SCHEMA
    return result


@router.get("/{mobil_id}", response_model=schemas.MobilResponse)
def get_car_detail(mobil_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == mobil_id, models.Car.status == "approved").first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
    showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first() if car.showroom_id else None
    data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"
    
    return schemas.MobilResponse(**data) # <-- PENTING: CAST KE SCHEMA
