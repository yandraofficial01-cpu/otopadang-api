import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Car
from schemas import CarCreate, CarResponse
from dependencies import get_current_user

router = APIRouter(prefix="/mobil", tags=["Cars"])

# 1. PUBLIK: BUAT otopadang.com
@router.get("/", response_model=List[CarResponse])
def get_all_cars_public(db: Session = Depends(get_db)):
    cars = db.query(Car).filter(Car.status.in_(['approved', 'ready'])).order_by(Car.created_at.desc()).all()
    return cars

# 2. DASHBOARD: BUAT SHOWROOM/ADMIN LOGIN
@router.get("/all", response_model=List[CarResponse])
def get_all_cars_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    showroom_id = current_user.get("showroom_id")
    query = db.query(Car)
    if role == "admin":
        cars = query.order_by(Car.created_at.desc()).all()
    else:
        cars = query.filter(Car.showroom_id == showroom_id).order_by(Car.created_at.desc()).all()
    return cars

# 3. DETAIL MOBIL
@router.get("/{car_id}", response_model=CarResponse)
def get_car_detail(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    if current_user.get("role")!= "admin" and car.showroom_id!= current_user.get("showroom_id"):
        raise HTTPException(status_code=403, detail="Akses ditolak. Ini bukan mobil anda")
    return car

# 4. CREATE: TERIMA JSON DARI FE + URL CLOUDINARY
@router.post("/", response_model=CarResponse, status_code=201)
async def create_car(
    car_data: CarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")
    user_showroom_id = current_user.get("showroom_id")

    if role == "showroom" and not user_showroom_id:
        raise HTTPException(status_code=403, detail="Akun showroom tidak punya showroom_id")

    car_dict = car_data.dict()
    # FE lu kirim 'dp', tapi DB lu namanya 'dp' udah ada. aman
    # Kalau DB lu namanya 'angsuran' bukan 'dp', hapus ini:
    # car_dict['angsuran'] = car_dict.pop('dp', None)

    new_car = Car(
        showroom_id = user_showroom_id if role == "showroom" else None,
        status='pending',
        **car_dict
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

# 5. UPDATE
@router.put("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: int,
    car_data: CarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    if current_user.get("role")!= "admin" and db_car.showroom_id!= current_user.get("showroom_id"):
        raise HTTPException(status_code=403, detail="Akses ditolak. Ini bukan mobil anda")

    update_data = car_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_car, key, value)

    db.commit()
    db.refresh(db_car)
    return db_car

# 6. DELETE
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
