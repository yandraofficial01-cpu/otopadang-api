import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Car
from schemas import CarResponse
from dependencies import get_current_user

router = APIRouter(prefix="/mobil", tags=["Cars"])

UPLOAD_DIR = "static/uploads/cars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. ENDPOINT PUBLIK BUAT OTOPADANG.COM
@router.get("/", response_model=List[CarResponse])
def get_all_cars_public(db: Session = Depends(get_db)):
    """
    Cuma nampilin mobil yg udah di approve admin dan status ready
    GAK PAKAI LOGIN
    """
    cars = db.query(Car).filter(Car.status.in_(['approved', 'ready'])).order_by(Car.created_at.desc()).all()
    return cars

# 2. ENDPOINT PRIVATE BUAT DASHBOARD SHOWROOM/ADMIN
@router.get("/all", response_model=List[CarResponse])
def get_all_cars_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Admin: liat semua status. Showroom: liat punya dia semua status
    """
    role = current_user.get("role")
    showroom_id = current_user.get("showroom_id")

    query = db.query(Car)

    if role == "admin":
        cars = query.order_by(Car.created_at.desc()).all()
    else: # role showroom
        cars = query.filter(Car.showroom_id == showroom_id).order_by(Car.created_at.desc()).all()

    return cars

@router.get("/{car_id}", response_model=CarResponse)
def get_car_detail(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    # CEK KEPEMILIKAN
    if current_user.get("role")!= "admin" and car.showroom_id!= current_user.get("showroom_id"):
        raise HTTPException(status_code=403, detail="Akses ditolak. Ini bukan mobil anda")

    return car

# 3. ENDPOINT INPUT MOBIL + UPLOAD 8 FOTO SEKALIGUS
@router.post("/", response_model=CarResponse, status_code=201)
async def create_car(
    # DATA MOBIL PAKAI FORM
    nama_mobil: str = Form(...),
    merek: str = Form(...),
    tipe: Optional[str] = Form(None),
    tahun: int = Form(...),
    kilometer: Optional[int] = Form(None),
    transmisi: Optional[str] = Form("Manual"),
    bahan_bakar: Optional[str] = Form("Bensin"),
    warna: Optional[str] = Form(None),
    harga: int = Form(...),
    harga_kredit: Optional[int] = Form(None),
    dp: Optional[int] = Form(None),
    lama_angsuran: Optional[int] = Form(None),
    lokasi: Optional[str] = Form(None),
    deskripsi: Optional[str] = Form(None),
    no_wa_showroom: str = Form(...),
    # FILE FOTO BISA BANYAK
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Showroom nambah mobil + upload 8 foto sekaligus"""
    role = current_user.get("role")
    user_showroom_id = current_user.get("showroom_id")

    if role == "showroom" and not user_showroom_id:
        raise HTTPException(status_code=403, detail="Akun showroom tidak punya showroom_id")

    # 1. UPLOAD FOTO KE FOLDER
    foto_urls = [None] * 8 # siapin 8 slot kosong
    for i, img in enumerate(images[:8]): # max 8
        ext = img.filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)
        foto_urls[i] = f"/static/uploads/cars/{filename}"

    # 2. BUAT OBJECT CAR BARU IKUTIN KOLOM DB LU
    new_car = Car(
        showroom_id = user_showroom_id if role == "showroom" else None,
        nama_mobil=nama_mobil,
        merek=merek,
        tipe=tipe,
        tahun=tahun,
        kilometer=kilometer,
        transmisi=transmisi,
        bahan_bakar=bahan_bakar,
        warna=warna,
        harga=harga,
        harga_kredit=harga_kredit,
        dp=dp,
        angsuran=None, # dihitung di FE atau BE terpisah
        lama_angsuran=lama_angsuran,
        lokasi=lokasi,
        deskripsi=deskripsi,
        no_wa_showroom=no_wa_showroom,
        foto_url_1=foto_urls[0],
        foto_url_2=foto_urls[1],
        foto_url_3=foto_urls[2],
        foto_url_4=foto_urls[3],
        foto_url_5=foto_urls[4],
        foto_url_6=foto_urls[5],
        foto_url_7=foto_urls[6],
        foto_url_8=foto_urls[7],
        status='pending' # default pending nunggu admin approve
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

@router.put("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: int,
    # Sama kayak create, tapi semua optional
    nama_mobil: Optional[str] = Form(None),
    merek: Optional[str] = Form(None),
    #...dst. Biar ga panjang, copy aja dari atas dan kasih Optional
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")

    if current_user.get("role")!= "admin" and db_car.showroom_id!= current_user.get("showroom_id"):
        raise HTTPException(status_code=403, detail="Akses ditolak. Ini bukan mobil anda")

    # Update data text
    for key, value in locals().items():
        if key not in ['car_id', 'images', 'db', 'current_user', 'db_car'] and value is not None:
            setattr(db_car, key, value)

    # Update foto baru kalau ada
    foto_slots = [db_car.foto_url_1, db_car.foto_url_2, db_car.foto_url_3, db_car.foto_url_4,
                  db_car.foto_url_5, db_car.foto_url_6, db_car.foto_url_7, db_car.foto_url_8]

    for i, img in enumerate(images[:8]):
        if img.filename: # kalau ada file baru
            ext = img.filename.split(".")[-1]
            filename = f"{uuid4()}.{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(img.file, buffer)
            url = f"/static/uploads/cars/{filename}"
            setattr(db_car, f'foto_url_{i+1}', url) # timpa dari slot 1

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
