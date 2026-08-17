from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas 
from database import get_db
from .admin_auth import require_admin, hash_password

router = APIRouter(prefix="/admin", tags=["Admin Showroom"])

@router.get("/showrooms", response_model=list[schemas.ShowroomResponse])
def get_all_showrooms(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Showroom).all()

@router.get("/showrooms-pending", response_model=list[schemas.ShowroomResponse])
def get_showrooms_pending(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Showroom).filter(models.Showroom.status == "pending").all()

@router.post("/register-showroom", response_model=schemas.ShowroomResponse)
def register_showroom_manual(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db)):
    db_showroom = db.query(models.Showroom).filter(models.Showroom.subdomain == showroom.subdomain).first()
    if db_showroom: raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")
    db_user = db.query(models.User).filter(models.User.email == showroom.email).first()
    if db_user: raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    hashed_password = hash_password(showroom.password)
    try:
        new_showroom = models.Showroom(**showroom.model_dump(exclude={"password", "email"}), status="pending", status_bayar="trial", paket="Free")
        db.add(new_showroom); db.commit(); db.refresh(new_showroom)

        new_user = models.User(showroom_id=new_showroom.id, email=showroom.email, password=hashed_password, name=showroom.nama_showroom, role='showroom', status='active')
        db.add(new_user); db.commit()
    except Exception as e:
        db.rollback(); raise HTTPException(status_code=500, detail=f"Gagal daftar: {str(e)}")
    return new_showroom

@router.put("/showrooms/{showroom_id}/approve")
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.status = "approved"; showroom.status_bayar = "aktif"; db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} berhasil di approve"}

@router.put("/showrooms/{showroom_id}/premium")
def set_premium(showroom_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.paket = "Premium"; showroom.status_bayar = "aktif"; db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} jadi Premium"}
