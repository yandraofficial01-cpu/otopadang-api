import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Car, User, Showroom
from schemas import CarCreate, CarResponse
from dependencies import get_current_user

router = APIRouter(prefix="/mobil", tags=["Cars"])

# 1. PUBLIK INDUK
@router.get("/all-public", response_model=List[CarResponse])
def get_all_cars_public(db: Session = Depends(get_db)):
    results = (
        db.query(Car, Showroom.nama_showroom.label("showroom_nama"), Showroom.wa_number.label("wa_showroom"))
      .outerjoin(Showroom, Car.showroom_id == Showroom.id)
      .filter(Car.status.in_(['approved', 'ready'])) # Publik cuma liat yg approved/ready
      .order_by(Car.created_at.desc())
      .all()
    )
    mobil_list = []
    for car, showroom_nama, wa_showroom in results:
        car_dict = CarResponse.model_validate(car).model_dump()
        car_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
        car_dict['wa_showroom'] = wa_showroom or "62812PUSAT"
        mobil_list.append(car_dict)
    return mobil_list

# 1.5 PUBLIK ANAK
@router.get("/showroom/{showroom_id}", response_model=List[CarResponse])
def get_cars_by_showroom_public(showroom_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(Car, Showroom.nama_showroom.label("showroom_nama"), Showroom.wa_number.label("wa_showroom"))
      .outerjoin(Showroom, Car.showroom_id == Showroom.id)
      .filter(Car.showroom_id == showroom_id, Car.status.in_(['approved', 'ready'])) # FIX: jangan 'sold'
      .order_by(Car.created_at.desc())
      .all()
    )
    mobil_list = []
    for car, showroom_nama, wa_showroom in results:
        car_dict = CarResponse.model_validate(car).model_dump()
        car_dict['showroom_nama'] = showroom_nama
        car_dict['wa_showroom'] = wa_showroom
        mobil_list.append(car_dict)
    return mobil_list

# 2. DASHBOARD
@router.get("/all", response_model=List[CarResponse])
def get_all_cars_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    role = current_user.role
    showroom_id = current_user.showroom_id
    query = db.query(Car)
    if role == "admin":
        cars = query.order_by(Car.created_at.desc()).all() # Admin liat semua
    else:
        cars = query.filter(Car.showroom_id == showroom_id).order_by(Car.created_at.desc()).all() # Showroom liat punya sendiri
    return cars

# 3. DETAIL MOBIL
@router.get("/{car_id}", response_model=CarResponse)
def get_car_detail(car_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Car, Showroom.nama_showroom.label("showroom_nama"), Showroom.wa_number.label("wa_showroom"))
      .outerjoin(Showroom, Car.showroom_id == Showroom.id)
      .filter(Car.id == car_id, Car.status.in_(['approved', 'ready']))
      .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    car, showroom_nama, wa_showroom = result
    car_dict = CarResponse.model_validate(car).model_dump()
    car_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
    car_dict['wa_showroom'] = wa_showroom or "62812PUSAT"
    return car_dict

# 4. CREATE - UDAH FIX
@router.post("/", response_model=CarResponse, status_code=201)
def create_car(car_data: CarCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_car = Car(
        **car_data.model_dump(),
        showroom_id=current_user.showroom_id, # otomatis ngambil dari yg login
        status="pending", # default pending
        created_at=datetime.utcnow()
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car # <-- INI YG KEMARIN KOSONG

# 5. UPDATE - UDAH FIX
@router.put("/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car_data: CarCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car: 
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    # Cek kepemilikan: showroom cuma bisa edit punya sendiri
    if current_user.role!= "admin" and car.showroom_id!= current_user.showroom_id:
        raise HTTPException(status_code=403, detail="Tidak punya akses")

    for key, value in car_data.model_dump(exclude_unset=True).items():
        setattr(car, key, value)
    
    db.commit()
    db.refresh(car)
    return car

# 6. DELETE - UDAH FIX
@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car: 
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    # Cek kepemilikan
    if current_user.role!= "admin" and car.showroom_id!= current_user.showroom_id:
        raise HTTPException(status_code=403, detail="Tidak punya akses")
        
    db.delete(car)
    db.commit()
    return {"message": "Mobil berhasil dihapus"}
