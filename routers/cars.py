from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from routers.auth_router import get_current_user # <-- UDAH BENER

router = APIRouter()

@router.post("/", response_model=schemas.MobilResponse)
def create_car(mobil: schemas.MobilCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 1. Cek role harus showroom
    if current_user.role.lower()!= "showroom":
        raise HTTPException(status_code=403, detail="Hanya showroom yang bisa input mobil")

    # 2. AMBIL SHOWROOM DARI current_user.showroom_id
    if not current_user.showroom_id:
        raise HTTPException(status_code=404, detail="Akun ini belum terhubung ke showroom. Hubungi admin")

    showroom = db.query(models.Showroom).filter(models.Showroom.id == current_user.showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Data showroom tidak ditemukan")

    # 3. Validasi wajib di backend juga
    if not mobil.nama_mobil or not mobil.merek or not mobil.harga or not mobil.foto_url_1:
        raise HTTPException(status_code=400, detail="Lengkapi Nama, Merek, Harga & Foto Cover")

    # 4. Simpan ke DB status = pending
    db_car = models.Car(
        **mobil.dict(),
        showroom_id = showroom.id,
        status = "pending" # <--- BARU INPUT = PENDING
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)

    # 5. Cast ke response biar ada showroom_nama
    data = {c.name: getattr(db_car, c.name) for c in db_car.__table__.columns}
    data['showroom_nama'] = showroom.nama_showroom

    return schemas.MobilResponse(**data)

@router.get("/my-cars", response_model=list[schemas.MobilResponse]) # <--- BARU: BUAT DASHBOARD SHOWROOM
def get_my_cars(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower()!= "showroom":
        raise HTTPException(status_code=403, detail="Hanya showroom")

    cars = db.query(models.Car).filter(models.Car.showroom_id == current_user.showroom_id).order_by(models.Car.id.desc()).all()

    result = []
    for car in cars:
        data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
        data['showroom_nama'] = current_user.showroom.nama_showroom
        result.append(schemas.MobilResponse(**data))
    return result

@router.get("/all-public", response_model=list[schemas.MobilResponse]) # <--- INI BUAT WEB INDUK
def get_cars_public(db: Session = Depends(get_db)):
    # HANYA TAMPIL YG APPROVED DAN BUKAN SOLD
    cars = db.query(models.Car).filter(models.Car.status == "approved", models.Car.status_jual!= "sold").order_by(models.Car.id.desc()).all()

    result = []
    for car in cars:
        data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
        showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first() if car.showroom_id else None
        data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"
        result.append(schemas.MobilResponse(**data))
    return result

@router.get("/{mobil_id}", response_model=schemas.MobilResponse)
def get_car_detail(mobil_id: int, db: Session = Depends(get_db)):
    car = db.query(models.Car).filter(models.Car.id == mobil_id).first() # <--- detail boleh lihat pending juga
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    data = {c.name: getattr(car, c.name) for c in car.__table__.columns}
    showroom = db.query(models.Showroom).filter(models.Showroom.id == car.showroom_id).first() if car.showroom_id else None
    data['showroom_nama'] = showroom.nama_showroom if showroom else "Admin Pusat"

    return schemas.MobilResponse(**data)

# ============ KHUS ADMIN ============
@router.put("/admin/{mobil_id}/approve")
def approve_car(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower()!= "admin":
        raise HTTPException(status_code=403, detail="Hanya admin")

    car = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not car: raise HTTPException(404, "Mobil tidak ditemukan")

    car.status = "approved" # <--- APPROVE
    db.commit()
    return {"message": "Mobil berhasil di-approve"}

@router.put("/admin/{mobil_id}/sold")
def mark_sold(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower()!= "admin":
        raise HTTPException(status_code=403, detail="Hanya admin")

    car = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not car: raise HTTPException(404, "Mobil tidak ditemukan")

    car.status_jual = "sold" # <--- TANDAI SOLD OUT
    db.commit()
    return {"message": "Mobil ditandai Sold Out"}

@router.delete("/admin/{mobil_id}")
def delete_car(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower()!= "admin":
        raise HTTPException(status_code=403, detail="Hanya admin")

    car = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not car: raise HTTPException(404, "Mobil tidak ditemukan")

    db.delete(car)
    db.commit()
    return {"message": "Mobil berhasil dihapus"}

# ============ KHUS SHOWROOM ============
@router.put("/{mobil_id}")
def update_car(mobil_id: int, mobil: schemas.MobilUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.lower()!= "showroom":
        raise HTTPException(status_code=403, detail="Hanya showroom")

    car = db.query(models.Car).filter(models.Car.id == mobil_id, models.Car.showroom_id == current_user.showroom_id).first()
    if not car: raise HTTPException(404, "Mobil tidak ditemukan atau bukan milik anda")

    # Showroom HANYA BOLEH EDIT 3 INI
    if mobil.harga is not None: car.harga = mobil.harga
    if mobil.no_wa is not None: car.no_wa = mobil.no_wa
    if mobil.spesifikasi is not None: car.spesifikasi = mobil.spesifikasi

    db.commit()
    db.refresh(car)
    return {"message": "Data mobil berhasil diupdate"}
