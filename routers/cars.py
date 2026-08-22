from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from .auth_router import get_current_user

router = APIRouter(prefix="/cars", tags=["Cars Showroom"])

# 1. SHOWROOM INPUT MOBIL BARU
@router.post("/", response_model=schemas.MobilResponse)
def create_car(
    car_data: schemas.MobilCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "showroom" or not current_user.showroom_id:
        raise HTTPException(status_code=403, detail="Cuma showroom yang bisa")
    
    car_dict = car_data.model_dump()
    
    # HAPUS FIELD YG KITA SET OTOMATIS BIAR GA BENTROK
    car_dict.pop("no_wa_showroom", None)
    car_dict.pop("status", None) 
    car_dict.pop("showroom_id", None)
    
    # ISI OTOMATIS
    if not car_data.no_wa_showroom: # kalau FE kosong
        car_dict["no_wa_showroom"] = current_user.showroom.wa_number
    else: # kalau FE isi manual
        car_dict["no_wa_showroom"] = car_data.no_wa_showroom
        
    db_car = models.Car(
        **car_dict, 
        showroom_id=current_user.showroom_id, 
        status="pending" # kita set sendiri
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# 2. SHOWROOM EDIT MOBIL SENDIRI
@router.put("/{mobil_id}", response_model=schemas.MobilResponse)
def update_car(
    mobil_id: int, 
    car_data: schemas.MobilUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "showroom": 
        raise HTTPException(status_code=403, detail="Cuma showroom")
    
    db_car = db.query(models.Car).filter(
        models.Car.id == mobil_id, 
        models.Car.showroom_id == current_user.showroom_id
    ).first()
    if not db_car: 
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    for key, value in car_data.model_dump(exclude_unset=True).items(): 
        setattr(db_car, key, value)
    
    db.commit()
    db.refresh(db_car)
    return db_car

# 3. PUBLIC LIHAT MOBIL YANG SUDAH APPROVED
@router.get("/all-public", response_model=list[schemas.MobilResponse])
def get_cars_public(db: Session = Depends(get_db)):
    cars = db.query(models.Car).filter(models.Car.status == "approved").all()
    return cars

# 4. SHOWROOM LIHAT MOBIL MILIK SENDIRI
@router.get("/my-cars", response_model=list[schemas.MobilResponse])
def get_my_cars(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "showroom": 
        raise HTTPException(status_code=403, detail="Cuma showroom")
    cars = db.query(models.Car).filter(models.Car.showroom_id == current_user.showroom_id).all()
    return cars
