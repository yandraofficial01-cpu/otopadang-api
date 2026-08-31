from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from routers.auth_router import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.MobilResponse) # INPUT BARU
def create_car(mobil: schemas.MobilCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower()!= "showroom":
        raise HTTPException(status_code=403, detail="Hanya showroom")

    if not current_user.showroom_id:
        raise HTTPException(status_code=404, detail="Akun belum terhubung ke showroom")

    showroom = db.query(models.Showroom).filter(models.Showroom.id == current_user.showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Data showroom tidak ditemukan")

    # FIX: BUANG status & status_jual dari body biar gak bentrok
    car_data = mobil.dict(exclude_unset=True)
    car_data.pop("status", None)
    car_data.pop("status_jual", None)

    db_car = models.Car(
        **car_data,
        showroom_id = showroom.id,
        status = "pending", # <--- KITA YANG SET
        status_jual = "tersedia" # <--- KITA YANG SET
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)

    data = {c.name: getattr(db_car, c.name) for c in db_car.__table__.columns}
    data['showroom_nama'] = showroom.nama_showroom
    return schemas.MobilResponse(**data)

@router.get("/my-cars", response_model=list[schemas.MobilResponse]) # LIHAT PUNYA SENDIRI
def get_my_cars(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower()!= "showroom":
        raise HTTPException(403, "Hanya showroom")

    cars = db.query(models.Car).filter(models.Car.showroom_id == current_user.showroom_id).order_by(models.Car.id.desc()).all()
    result = []
    for car in cars:
        data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
        data['showroom_nama'] = current_user.showroom.nama_showroom if current_user.showroom else "Admin Pusat"
        result.append(schemas.MobilResponse(**data))
    return result

@router.put("/{mobil_id}") # EDIT TERBATAS
def update_car(mobil_id: int, mobil: schemas.MobilUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower()!= "showroom":
        raise HTTPException(403, "Hanya showroom")

    car = db.query(models.Car).filter(models.Car.id == mobil_id, models.Car.showroom_id == current_user.showroom_id).first()
    if not car:
        raise HTTPException(404, "Mobil tidak ditemukan atau bukan milik anda")

    update_data = mobil.dict(exclude_unset=True)

    # Showroom HANYA BOLEH EDIT 4 INI
    if "harga" in update_data: car.harga = update_data["harga"]
    if "no_wa_showroom" in update_data: car.no_wa_showroom = update_data["no_wa_showroom"] # <--- FIX: no_wa -> no_wa_showroom
    if "deskripsi" in update_data: car.deskripsi = update_data["deskripsi"]
    if "spesifikasi" in update_data: car.spesifikasi = update_data["spesifikasi"]

    db.commit()
    db.refresh(car)
    return {"message": "Data mobil berhasil diupdate", "data": schemas.MobilResponse.from_orm(car)}

@router.get("/all-public", response_model=list[schemas.MobilResponse]) # BUAT WEB INDUK
def get_cars_public(db: Session = Depends(get_db)):
    # HANYA TAMPIL YG APPROVED DAN BELUM SOLD
    cars = db.query(models.Car).filter(models.Car.status == "approved", models.Car.status_jual!= "sold").order_by(models.Car.id.desc()).all()
    result = []
    for car in cars:
        data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
        showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first()
        data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"
        result.append(schemas.MobilResponse(**data))
    return result

@router.get("/{mobil_id}", response_model=schemas.MobilResponse) # DETAIL
def get_car_detail(mobil_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
    showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first()
    data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"

    return schemas.MobilResponse(**data)
