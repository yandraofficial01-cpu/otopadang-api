from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routers.admin_auth import require_admin
from database import get_db
from models import Showroom, User
from schemas import RegisterShowroomRequest
from passlib.context import CryptContext

router = APIRouter() # KOSONG KARENA PREFIX UDAH DI MAIN

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password): 
    return pwd_context.hash(password)

@router.get("/admin/showroom/")
def get_all_showroom(db: Session = Depends(get_db), admin = Depends(require_admin)):
    showrooms = db.query(Showroom).order_by(Showroom.id.desc()).all()
    return showrooms

@router.post("/admin/register-showroom")
def register_showroom(data: RegisterShowroomRequest, db: Session = Depends(get_db)):
    # 1. Cek subdomain
    existing_sub = db.query(Showroom).filter(Showroom.subdomain == data.subdomain).first()
    if existing_sub:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")
    
    # 2. Cek email
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # 3. Buat Showroom DULU biar dapet ID
    new_showroom = Showroom(
        nama_showroom=data.nama_showroom,
        subdomain=data.subdomain,
        alamat=data.alamat,
        wa_number=data.wa_number,
        logo=data.logo,
        deskripsi=data.deskripsi,
        status="pending",
        paket="Gratis",
        status_bayar="belum_bayar"
    )
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom) # WAJIB biar dapet new_showroom.id

    # 4. Baru Buat User pake showroom_id
    new_user = User(
        showroom_id=new_showroom.id,
        name=data.nama_showroom,
        email=data.email,
        password=get_password_hash(data.password), # FIX: password bukan hashed_password
        phone=data.wa_number, # optional, biar sekalian
        role="showroom",
        status="pending"
    )
    db.add(new_user)
    db.commit()

    return {
        "message": "Registrasi Berhasil! Menunggu approval admin",
        "data": {
            "nama_showroom": new_showroom.nama_showroom,
            "subdomain": new_showroom.subdomain,
            "url": f"https://{new_showroom.subdomain}.otopadang.com"
        }
    }

@router.put("/admin/showroom/{showroom_id}/approve")
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    showroom.status = "approved"
    db.commit()
    db.refresh(showroom)
    return {"message": f"Showroom {showroom.nama_showroom} berhasil di approve", "data": showroom}

@router.put("/admin/showroom/{showroom_id}/premium")
def set_premium(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    showroom.paket = "Premium"
    db.commit()
    db.refresh(showroom)
    return {"message": f"Showroom {showroom.nama_showroom} sudah Premium", "data": showroom}

@router.delete("/admin/showroom/{showroom_id}")
def delete_showroom(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    # Hapus user dulu biar ga error foreign key
    db.query(User).filter(User.showroom_id == showroom_id).delete()
    
    db.delete(showroom)
    db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} berhasil dihapus"}
