from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import models, schemas 
from database import get_db
from routers.auth_router import get_current_user # PAKE DARI SINI

router = APIRouter(prefix="/admin", tags=["Admin"])

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# FUNCTION CEK ADMIN PUSAT
def require_admin(current_user: models.UserShowroom = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.showroom_id is not None: # Admin pusat harus NULL
        raise HTTPException(status_code=403, detail="Akses khusus Admin Pusat")
    return current_user

# ===============================
# 1. SHOWROOM
# ===============================
@router.get("/showrooms", response_model=list[schemas.ShowroomResponse])
def get_all_showrooms(db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    return db.query(models.Showroom).all()

@router.get("/showrooms-pending", response_model=list[schemas.ShowroomResponse])
def get_showrooms_pending(db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    return db.query(models.Showroom).filter(models.Showroom.status == "pending").all()

@router.post("/register-showroom", response_model=schemas.ShowroomResponse)
def register_showroom_manual(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    db_showroom = db.query(models.Showroom).filter(models.Showroom.subdomain == showroom.subdomain).first()
    if db_showroom:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")

    db_user = db.query(models.UserShowroom).filter(models.UserShowroom.email == showroom.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    hashed_password = hash_password(showroom.password)

    new_showroom = models.Showroom(
        nama_showroom=showroom.nama_showroom,
        subdomain=showroom.subdomain,
        wa_number=showroom.wa_number,
        alamat=showroom.alamat,
        deskripsi=showroom.deskripsi,
        logo=showroom.logo,
        status="approved",
        status_bayar="aktif",
        # HAPUS: status_akun="aktif",
        paket="Premium"
    )
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)

    new_user = models.UserShowroom(
        showroom_id=new_showroom.id,
        email=showroom.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    return new_showroom

@router.put("/showrooms/{showroom_id}/approve")
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.status = "approved"
    showroom.status_bayar = "aktif"
    db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} berhasil di approve"}

# ... sisanya sama, tinggal copas

# ===============================
# 2. MOBIL - GANTI Mobil -> Car
# ===============================
@router.get("/mobil", response_model=list[schemas.MobilResponse])
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    return db.query(models.Car).all() # FIX

@router.put("/mobil/{mobil_id}")
def update_mobil_status(mobil_id: int, data: dict, db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first() # FIX
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    for key, value in data.items():
        setattr(mobil, key, value)
    db.commit()
    return {"message": f"Status mobil diupdate"}

# ===============================
# 3. RUMAH - GANTI Rumah -> House
# ===============================
@router.get("/rumah", response_model=list[schemas.RumahResponse])
def get_all_rumah_admin(db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    return db.query(models.House).all() # FIX

@router.post("/upload-rumah", response_model=schemas.RumahResponse)
def upload_rumah(data: schemas.RumahCreate, db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    new_rumah = models.House(**data.model_dump()) # FIX
    db.add(new_rumah)
    db.commit()
    db.refresh(new_rumah)
    return new_rumah

@router.put("/rumah/{rumah_id}")
def update_rumah_status(rumah_id: int, data: dict, db: Session = Depends(get_db), current_user: models.UserShowroom = Depends(require_admin)):
    rumah = db.query(models.House).filter(models.House.id == rumah_id).first() # FIX
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    for key, value in data.items():
        setattr(rumah, key, value)
    db.commit()
    return {"message": f"Status rumah diupdate"}
