import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Car, User
from schemas import CarCreate, CarResponse
from dependencies import get_current_user

router = APIRouter(prefix="/mobil", tags=["Cars"])

# 1. PUBLIK INDUK: BUAT otopadang.com - HARUS APPROVED DULU
@router.get("/all-public", response_model=List[CarResponse])
def get_all_cars_public(db: Session = Depends(get_db)):
    results = db.query(Car, User.name.label("showroom_nama"), User.wa_number.label("wa_showroom")) \
      .outerjoin(User, Car.showroom_id == User.showroom_id) \
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
    results = db.query(Car, User.name.label("showroom_nama"), User.wa_number.label("wa_showroom")) \
      .outerjoin(User, Car.showroom_id == User.showroom_id) \
      .filter(Car.showroom_id == showroom_id, Car.status!= 'sold') \
      .order_by(Car.created_at.desc()).all()

    mobil_list = []
    for car, showroom_nama, wa_showroom in results:
        car_dict = CarResponse.model_validate(car).model_dump()
        car_dict['showroom_nama'] = showroom_nama
        car_dict['wa_showroom'] = wa_showroom
        mobil_list.append(car_dict)
    return mobil_list

# 2. DASHBOARD: BUAT SHOWROOM/ADMIN LOGIN
@router.get("/all", response_model=List[CarResponse])
def get_all_cars_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
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
def get_car_detail(
    car_id: int,
    db: Session = Depends(get_db)
):
    result = db.query(Car, User.name.label("showroom_nama"), User.wa_number.label("wa_showroom")) \
      .outerjoin(User, Car.showroom_id == User.showroom_id) \
      .filter(Car.id == car_id, Car.status.in_(['approved', 'ready'])) \
      .first()

    if not result:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    car, showroom_nama, wa_showroom = result
    car_dict = CarResponse.model_validate(car).model_dump()
    car_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
    car_dict['wa_showroom'] = wa_showroom or "62812PUSAT"
    return car_dict

# 4. CREATE
@router.post("/", response_model=CarResponse, status_code=201)
async def create_car(car_data: CarCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    role = current_user.role
    user_showroom_id = current_user.showroom_id

    if role == "showroom" and not user_showroom_id:
        raise HTTPException(status_code=403, detail="Akun showroom tidak punya showroom_id")

    car_dict = car_data.model_dump() # ganti.dict() ke.model_dump() kalau pake pydantic v2

    new_car = Car(
        showroom_id = user_showroom_id if role == "showroom" else car_data.showroom_id,
        status='pending',
        **car_dict
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

# 5. UPDATE
@router.put("/{car_id}", response_model=CarResponse)
async def update_car(car_id: int, car_data: CarCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    if current_user.role!= "admin" and db_car.showroom_id!= current_user.showroom_id:
        raise HTTPException(status_code=403, detail="Akses ditolak")

    update_data = car_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)
    return db_car

# 6. DELETE
@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    if current_user.role!= "admin" and db_car.showroom_id!= current_user.showroom_id:
        raise HTTPException(status_code=403, detail="Akses ditolak")
    db.delete(db_car)
    db.commit()
    return {"message": "Mobil berhasil dihapus"}
