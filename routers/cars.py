import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Car
from schemas import CarCreate, CarResponse
from dependencies import get_current_user

router = APIRouter(prefix="/mobil", tags=["Cars"])

UPLOAD_DIR = "static/uploads/cars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. ENDPOINT PUBLIK BUAT INDUK WEB OTOPADANG.COM
@router.get("/", response_model=List[CarResponse])
def get_all_cars_public(db: Session = Depends(get_db)):
    """
    INI BUAT OTOPADANG.COM
    Cuma nampilin mobil yg udah di approve admin dan status ready
    GAK PAKAI LOGIN
    """
    cars = db.query(Car).filter(Car.status.in_(['approved', 'ready'])).order_by(Car.created_at.desc()).all()
    return cars

# 2. ENDPOINT PRIVATE BUAT DASHBOARD SHOWROOM
@router.get("/all", response_model=List[CarResponse])
def get_all_cars_admin(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # WAJIB LOGIN
):
    """
    INI BUAT DASHBOARD SHOWROOM
    Admin: liat semua status. Showroom: liat punya dia semua status
    """
    role = current_user.get("role")
    showroom_id = current_user.get("showroom_id")

    query = db.query(Car)

    if role == "admin":
        cars = query.filter(Car.status.in_(['approved', 'ready', 'sold', 'pending'])).all()
    else: # role showroom
        cars = query.filter(Car.showroom_id == showroom_id).all()

    return cars

@router.get("/{car_id}", response_model=CarResponse)
def get_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # INI TETEP DIKUNCI
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    # CEK KEPEMILIKAN
    if current_user.get("role")!= "admin" and car.showroom_id!= current_user.get("showroom_id"):
        raise HTTPException(status_code=403, detail="Akses ditolak. Ini bukan mobil anda")

    return car

@router.post("/", response_model=CarResponse, status_code=201)
def create_car(
    car: CarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Showroom nambah mobil. Auto masuk ke showroom_id dia"""
    role = current_user.get("role")
    showroom_id = current_user.get("showroom_id")

    if role!= "admin":
        car.showroom_id = showroom_id

    new_car = Car(**car.dict())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

@router.put("/{car_id}", response_model=CarResponse)
def update_car(
    car_id: int,
    car_update: CarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    if current_user.get("role")!= "admin" and db_car.showroom_id!= current_user.get("showroom_id"):
        raise HTTPException(status_code=403, detail="Akses ditolak. Ini bukan mobil anda")

    for key, value in car_update.dict().items():
        setattr(db_car, key, value)

    db.commit()
    db.refresh(db_car)
    return db_car

@router.delete("/{car_id}")
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    if current_user.get("role")!= "admin" and db_car.showroom_id!= current_user.get("showroom_id"):
        raise HTTPException(status_code=403, detail="Akses ditolak. Ini bukan mobil anda")

    db.delete(db_car)
    db.commit()
    return {"message": "Mobil berhasil dihapus"}

@router.post("/{car_id}/upload-foto")
async def upload_foto_mobil(
    car_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    if current_user.get("role")!= "admin" and car.showroom_id!= current_user.get("showroom_id"):
        raise HTTPException(status_code=403, detail="Akses ditolak. Ini bukan mobil anda")

    ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    url = f"/static/uploads/cars/{filename}"

    for i in range(1, 9):
        field = f"foto_url_{i}"
        if getattr(car, field) in [None, ""]:
            setattr(car, field, url)
            db.commit()
            db.refresh(car)
            return {"message": "Upload sukses", "url": url, "slot": i, "car": car}

    raise HTTPException(status_code=400, detail="Slot foto sudah penuh 8/8")
