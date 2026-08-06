from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import models, schemas 
from database import get_db
from dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# ===============================
# 1. SHOWROOM - BUAT MENU ADMIN
# ===============================
@router.get("/showrooms", response_model=list[schemas.ShowroomResponse])
def get_all_showrooms(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Buat menu Premium. Liat semua showroom"""
    showrooms = db.query(models.Showroom).all()
    return showrooms

@router.get("/showrooms-pending", response_model=list[schemas.ShowroomResponse])
def get_showrooms_pending(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Menu buat liat showroom yg daftar dari public"""
    showrooms = db.query(models.Showroom).filter(models.Showroom.status == "pending").all()
    return showrooms

@router.post("/register-showroom", response_model=schemas.ShowroomResponse)
def register_showroom_manual(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Khusus admin. Langsung approved + aktif"""
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
        status_akun="aktif",
        paket="Premium" # Admin daftarin langsung premium
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
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: 
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    if showroom.status == "approved":
        raise HTTPException(status_code=400, detail="Showroom sudah di approve")
        
    showroom.status = "approved"
    showroom.status_bayar = "aktif"
    db.commit()
    db.refresh(showroom)
    return {"message": f"Showroom {showroom.nama_showroom} berhasil di approve"}

@router.put("/showrooms/{showroom_id}/reject")
def reject_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: 
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.status = "rejected"
    db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} ditolak"}

@router.put("/showrooms/{showroom_id}/suspend")
def suspend_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Tombol SUSPEND. Buat matiin web showroom"""
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: 
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.status_bayar = "suspended" # <-- GANTI JADI INI
    db.commit()
    db.refresh(showroom)
    return {"message": f"Showroom {showroom.nama_showroom} di suspend"}

@router.put("/showrooms/{showroom_id}/activate")
def activate_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Tombol AKTIFKAN. Buat nyalain lagi web showroom"""
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: 
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.status_bayar = "aktif"
    db.commit()
    db.refresh(showroom)
    return {"message": f"Showroom {showroom.nama_showroom} diaktifkan"}

# ===============================
# 2. MOBIL - BUAT MENU ADMIN
# ===============================
@router.get("/mobil", response_model=list[schemas.MobilResponse])
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Ambil semua data mobil buat di approve"""
    return db.query(models.Mobil).all()

@router.put("/mobil/{mobil_id}")
def update_mobil_status(mobil_id: int, data: dict, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    mobil = db.query(models.Mobil).filter(models.Mobil.id == mobil_id).first()
    if not mobil: 
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    for key, value in data.items():
        setattr(mobil, key, value)
    db.commit()
    db.refresh(mobil)
    return {"message": f"Status mobil diupdate"}

# ===============================
# 3. RUMAH - BUAT MENU ADMIN
# ===============================
@router.get("/rumah", response_model=list[schemas.RumahResponse])
def get_all_rumah_admin(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Ambil semua data rumah"""
    return db.query(models.Rumah).all()

@router.post("/upload-rumah", response_model=schemas.RumahResponse)
def upload_rumah(data: schemas.RumahCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin upload rumah. Langsung approved"""
    new_rumah = models.Rumah(**data.model_dump(), status = "approved")
    db.add(new_rumah)
    db.commit()
    db.refresh(new_rumah)
    return new_rumah

@router.put("/rumah/{rumah_id}")
def update_rumah_status(rumah_id: int, data: dict, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    rumah = db.query(models.Rumah).filter(models.Rumah.id == rumah_id).first()
    if not rumah: 
        raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    for key, value in data.items():
        setattr(rumah, key, value)
    db.commit()
    db.refresh(rumah)
    return {"message": f"Status rumah diupdate"}
