from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas 
from database import get_db
from dependencies import require_admin # <-- WAJIB IMPORT INI

router = APIRouter(prefix="/admin", tags=["Admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register-showroom", response_model=schemas.ShowroomResponse)
def register_showroom_manual(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """
    Ini khusus kamu yg pake. Langsung approved. 
    Buat daftarin showroom rekanan tanpa nunggu
    """
    # 1. Cek subdomain
    db_showroom = db.query(models.Showroom).filter(models.Showroom.subdomain == showroom.subdomain).first()
    if db_showroom:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")

    # 2. Cek email
    db_user = db.query(models.UserShowroom).filter(models.UserShowroom.email == showroom.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # 3. Hash password
    hashed_password = hash_password(showroom.password)

    # 4. Buat Showroom - LANGSUNG APPROVED
    new_showroom = models.Showroom(
        nama_showroom=showroom.nama_showroom,
        subdomain=showroom.subdomain,
        wa_number=showroom.wa_number,
        alamat=showroom.alamat,
        deskripsi=showroom.deskripsi,
        logo=showroom.logo,
        status="approved" # <-- KUNCI: Langsung approved karena kamu yg daftarin
    )
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)

    # 5. Buat User Showroom
    new_user = models.UserShowroom(
        showroom_id=new_showroom.id,
        email=showroom.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()

    return new_showroom

@router.get("/showrooms-pending", response_model=list[schemas.ShowroomResponse])
def get_showrooms_pending(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Menu buat liat showroom yg daftar dari public"""
    showrooms = db.query(models.Showroom).filter(models.Showroom.status == "pending").all()
    return showrooms

@router.put("/showrooms/{showroom_id}/approve")
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Tombol APPROVE. Klik ini baru showroom bisa login"""
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: 
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    if showroom.status == "approved":
        raise HTTPException(status_code=400, detail="Showroom sudah di approve")
        
    showroom.status = "approved"
    db.commit()
    db.refresh(showroom)
    return {"message": f"Showroom {showroom.nama_showroom} berhasil di approve"}

@router.put("/showrooms/{showroom_id}/reject")
def reject_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Tombol TOLAK"""
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: 
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
        
    showroom.status = "rejected"
    db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} ditolak"}

@router.get("/mobil") # <-- Admin bisa liat semua mobil
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return db.query(models.Mobil).all()

@router.get("/rumah") # <-- Admin bisa liat semua rumah
def get_all_rumah_admin(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    return db.query(models.Rumah).all()

@router.post("/upload-rumah") 
def upload_rumah():
    return {"msg": "Endpoint upload rumah. Nanti kita isi"}
