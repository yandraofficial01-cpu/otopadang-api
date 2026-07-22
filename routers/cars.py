import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Car
from schemas import CarCreate, Car as CarSchema

router = APIRouter(tags=["Cars"]) # prefix="/cars" udah di main.py

UPLOAD_DIR = "static/uploads/cars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[CarSchema])
def get_all_cars(db: Session = Depends(get_db)):
    # GANTI: biar 'ready' juga muncul di frontend
    cars = db.query(Car).filter(Car.status.in_(['approved', 'ready'])).all()
    return cars

@router.get("/{car_id}", response_model=CarSchema)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    return car

@router.post("/", response_model=CarSchema)
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    new_car = Car(**car.dict())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

@router.put("/{car_id}", response_model=CarSchema)
def update_car(car_id: int, car_update: CarCreate, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    for key, value in car_update.dict().items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)
    return db_car

@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    db.delete(db_car)
    db.commit()
    return {"message": "Mobil berhasil dihapus"}


# TAMBAH INI: ENDPOINT UPLOAD FOTO
@router.post("/{car_id}/upload-foto")
async def upload_foto_mobil(
    car_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    # bikin nama file unik
    ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # simpan file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    url = f"/static/uploads/cars/{filename}"
    
    # cari slot foto kosong pertama dari 1-8
    for i in range(1, 9):
        field = f"foto_url_{i}"
        if getattr(car, field) in [None, ""]:
            setattr(car, field, url)
            db.commit()
            db.refresh(car)
            return {"message": "Upload sukses", "url": url, "slot": i, "car": car}
    
    raise HTTPException(status_code=400, detail="Slot foto sudah penuh 8/8")
