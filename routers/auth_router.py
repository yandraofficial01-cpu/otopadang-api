from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import UserShowroom, Showroom
from routers.admin_router import verify_password, get_password_hash # pastiin ini ada di admin_router
from dependencies import create_access_token # import dari root
import schemas

router = APIRouter(prefix="/auth", tags=["Auth Showroom"])

ADMIN_EMAILS = ["admin@otopadang.com", "yandraofficial01@gmail.com"]

@router.post("/register-showroom", status_code=201)
def register_showroom(data: schemas.RegisterShowroomRequest, db: Session = Depends(get_db)):
    """Daftar showroom baru. Status default = pending"""
    
    # 1. Cek email udah ada apa belum
    db_user = db.query(UserShowroom).filter(UserShowroom.email == data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    
    # 2. Cek subdomain udah ada apa belum
    db_showroom = db.query(Showroom).filter(Showroom.subdomain == data.subdomain).first()
    if db_showroom:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")
        
    # 3. Bikin data showroom baru status pending
    new_showroom = Showroom(
        nama_showroom = data.nama_showroom,
        subdomain = data.subdomain,
        alamat = data.alamat,
        wa_number = data.wa_number,
        status = "pending" # <-- KUNCI: nunggu di approve admin
    )
    db.add(new_showroom)
    db.commit()
    db.refresh(new_showroom)
    
    # 4. Bikin user login untuk showroom tsb
    hashed_password = get_password_hash(data.password)
    new_user = UserShowroom(
        email = data.email,
        password = hashed_password,
        showroom_id = new_showroom.id
    )
    db.add(new_user)
    db.commit()
    
    return {"message": "Pendaftaran berhasil. Menunggu persetujuan Admin Otopadang"}

@router.post("/login")
def login_showroom(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserShowroom).filter(UserShowroom.email == data.email).first()
    if not db_user or not verify_password(data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    showroom = db.query(Showroom).filter(Showroom.id == db_user.showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    
    # 1. CEK STATUS APPROVE DULU BRO
    if showroom.status != "approved" and db_user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Akun showroom belum disetujui admin")

    # 2. TENTUIN ROLE
    if db_user.email in ADMIN_EMAILS:
        role = "admin"
    else:
        role = "showroom"
        
    # 3. BIKIN TOKEN JWT
    token_data = {
        "user_id": db_user.id,
        "email": db_user.email,
        "role": role,
        "showroom_id": showroom.id
    }
    access_token = create_access_token(token_data)

    return {
        "message": "Login Berhasil", 
        "access_token": access_token, # <-- GANTI JADI JWT
        "token_type": "bearer",
        "showroom_id": showroom.id,
        "subdomain": showroom.subdomain,
        "nama_showroom": showroom.nama_showroom,
        "email": db_user.email,
        "role": role
    }
