import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Car, User, Showroom # TAMBAH SHOWROOM
from schemas import CarCreate, CarResponse
from dependencies import get_current_user

router = APIRouter(prefix="/mobil", tags=["Cars"])

# 1. PUBLIK INDUK: BUAT otopadang.com
@router.get("/all-public", response_model=List[CarResponse])
def get_all_cars_public(db: Session = Depends(get_db)):
    results = db.query(Car, Showroom.nama_showroom.label("showroom_nama"), Showroom.wa_number.label("wa_showroom")) \
     .outerjoin(Showroom, Car.showroom_id == Showroom.id) \ # JOIN KE SHOWROOM BUKAN USER
     .filter(Car.status.in_(['approved', 'ready'])) \
     .order_by(Car.created_at.desc()).all()

    mobil_list = []
    for car, showroom_nama, wa_showroom in results:
        car_dict = CarResponse.model_validate(car).model_dump()
        car_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
        car_dict['wa_showroom'] = wa_showroom or "62812PUSAT"
        mobil_list.append(car_dict)
    return mobil_list

# 1.5 PUBLIK ANAK: BUAT WEBSITE SHOWROOM
@router.get("/showroom/{showroom_id}", response_model=List[CarResponse])
def get_cars_by_showroom_public(showroom_id: int, db: Session = Depends(get_db)):
    results = db.query(Car, Showroom.nama_showroom.label("showroom_nama"), Showroom.wa_number.label("wa_showroom")) \
     .outerjoin(Showroom, Car.showroom_id == Showroom.id) \
     .filter(Car.showroom_id == showroom_id, Car.status!= 'sold') \
     .order_by(Car.created_at.desc()).all()

    mobil_list = []
    for car, showroom_nama, wa_showroom in results:
        car_dict = CarResponse.model_validate(car).model_dump()
        car_dict['showroom_nama'] = showroom_nama
        car_dict['wa_showroom'] = wa_showroom
        mobil_list.append(car_dict)
    return mobil_list

# 2. DASHBOARD
@router.get("/all", response_model=List[CarResponse])
def get_all_cars_dashboard(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    role = current_user.role
    showroom_id = current_user.showroom_id
    query = db.query(Car)
    if role == "admin":
        cars = query.order_by(Car.created_at.desc()).all()
    else:
        cars = query.filter(Car.showroom_id == showroom_id).order_by(Car.created_at.desc()).all()
    return cars

# 3. DETAIL MOBIL - PUBLIC
@router.get("/{car_id}", response_model=CarResponse)
def get_car_detail(car_id: int, db: Session = Depends(get_db)):
    result = db.query(Car, Showroom.nama_showroom.label("showroom_nama"), Showroom.wa_number.label("wa_showroom")) \
     .outerjoin(Showroom, Car.showroom_id == Showroom.id) \
     .filter(Car.id == car_id, Car.status.in_(['approved', 'ready'])) \
     .first()

    if not result:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    car, showroom_nama, wa_showroom = result
    car_dict = CarResponse.model_validate(car).model_dump()
    car_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
    car_dict['wa_showroom'] = wa_showroom or "62812PUSAT"
    return car_dict

# 4. 5. 6. CREATE UPDATE DELETE TETAP KODE LU
