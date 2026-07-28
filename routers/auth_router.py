from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import UserShowroom, Showroom
from auth import verify_password # cuma butuh verify
import schemas

router = APIRouter(prefix="/auth", tags=["Auth Showroom"])

@router.post("/login")
def login_showroom(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserShowroom).filter(UserShowroom.email == data.email).first()
    if not db_user or not verify_password(data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    showroom = db.query(Showroom).filter(Showroom.id == db_user.showroom_id).first()
    return {
        "message": "Login Berhasil", 
        "showroom_id": showroom.id,
        "subdomain": showroom.subdomain,
        "nama_showroom": showroom.nama_showroom
    }
