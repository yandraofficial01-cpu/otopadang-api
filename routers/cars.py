from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from auth_router import get_current_user # buat ambil user dari token

router = APIRouter()

@router.post("/", response_model=schemas.MobilResponse)
def create_car(mobil: schemas.MobilCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 1. Cek role harus showroom
    if current_user.role.lower() != "showroom":
        raise HTTPException(status_code=403, detail="Hanya showroom yang bisa input mobil")

    # 2. Ambil data showroom dari user yang login
    showroom = db.query(models.Showroom).filter(models.Showroom.user_id == current_user.id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Data showroom tidak ditemukan. Hubungi admin")

    # 3. Validasi wajib di backend juga
    if not mobil.nama_mobil or not mobil.merek or not mobil.harga or not mobil.foto_url_1:
        raise HTTPException(status_code=400, detail="Lengkapi Nama, Merek, Harga & Foto Cover")

    # 4. Simpan ke DB, status langsung pending biar di approve admin
    db_car = models.Car(
        **mobil.dict(),
        showroom_id = showroom.id,
        status = "pending"
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    
    # 5. Cast ke response biar ada showroom_nama
    data = {c.name: getattr(db_car, c.name) for c in db_car.__table__.columns}
    data['showroom_nama'] = showroom.nama_showroom
    
    return schemas.MobilResponse(**data)

@router.get("/all-public", response_model=list[schemas.MobilResponse])
def get_cars_public(db: Session = Depends(get_db)):
    cars = db.query(models.Car).filter(models.Car.status == "approved").order_by(models.Car.id.desc()).all()
    
    result = []
    for car in cars:
        data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
        showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first() if car.showroom_id else None
        data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"
        result.append(schemas.MobilResponse(**data))
    return result

@router.get("/{mobil_id}", response_model=schemas.MobilResponse)
def get_car_detail(mobil_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == mobil_id, models.Car.status == "approved").first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
    showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first() if car.showroom_id else None
    data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"
    
    return schemas.MobilResponse(**data)
