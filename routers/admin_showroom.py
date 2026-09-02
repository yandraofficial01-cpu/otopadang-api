from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload # TAMBAH joinedload
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
    # FIX: GANTI user -> users
    showrooms = db.query(Showroom).options(joinedload(Showroom.users)).order_by(Showroom.id.desc()).all()
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
    db.refresh(new_showroom)

    # 4. Baru Buat User pake showroom_id
    new_user = User(
        showroom_id=new_showroom.id,
        name=data.nama_showroom,
        email=data.email,
        password=get_password_hash(data.password),
        phone=data.wa_number,
        role="showroom",
        status="pending" # default pending
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
    
    # 1. APPROVE SHOWROOM
    showroom.status = "approved"
    
    # 2. LANGSUNG APPROVE USER JUGA
    user = db.query(User).filter(User.showroom_id == showroom_id).first()
    if user:
        user.status = "approved" # UDAH SAMA
    else:
        raise HTTPException(status_code=404, detail="User untuk showroom ini tidak ditemukan")
    
    db.commit()
    db.refresh(showroom)
    return {
        "message": f"Showroom {showroom.nama_showroom} & User berhasil diaktifkan", 
        "data": showroom
    }

@router.put("/admin/user/{user_id}/status") # ENDPOINT BARU BUAT STEL DARI FE
def update_user_status(user_id: int, new_status: str, db: Session = Depends(get_db), admin = Depends(require_admin)):
    """
    Body: { "new_status": "approved" } atau { "new_status": "pending" }
    """
    if new_status not in ["approved", "pending"]:
        raise HTTPException(status_code=400, detail="Status harus approved atau pending")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    user.status = new_status
    db.commit()
    
    return {"message": f"Status user {user.email} diubah jadi {new_status}"}

@router.put("/admin/showroom/{showroom_id}/paket")
def update_paket(showroom_id: int, data: dict, db: Session = Depends(get_db), admin = Depends(require_admin)):
    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    paket_baru = data.get('paket')
    if paket_baru not in ['Premium', 'Gratis']:
        raise HTTPException(status_code=400, detail="Paket harus Premium atau Gratis")
    
    showroom.paket = paket_baru
    db.commit()
    db.refresh(showroom)
    return {"message": f"Paket {showroom.nama_showroom} diubah ke {showroom.paket}", "data": showroom}

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
