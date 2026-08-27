from fastapi import APIRouter, Depends, HTTPException # TAMBAH HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter() # PREFIX KOSONG. Nanti diset di main.py jadi /cars

# 1. PUBLIC LIHAT MOBIL YANG SUDAH APPROVED
@router.get("/all-public", response_model=list[schemas.MobilResponse])
def get_cars_public(db: Session = Depends(get_db)):
    cars = db.query(models.Car).filter(models.Car.status == "approved").order_by(models.Car.id.desc()).all()
    
    result = []
    for car in cars:
        # Ubah object jadi dict
        data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
        
        # Ambil nama showroom manual biar gak crash FK
        if car.showroom_id:
            showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first()
            data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"
        else:
            data['showroom_nama'] = "Admin Pusat"
            
        result.append(data)
    return result


# 2. PUBLIC LIHAT DETAIL 1 MOBIL
@router.get("/{mobil_id}", response_model=schemas.MobilResponse)
def get_car_detail(mobil_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(
        models.Car.id == mobil_id, 
        models.Car.status == "approved"
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    # Ubah object jadi dict + isi showroom_nama
    data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
    if car.showroom_id:
        showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first()
        data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"
    else:
        data['showroom_nama'] = "Admin Pusat"
        
    return data
