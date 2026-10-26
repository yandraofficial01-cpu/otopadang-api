from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.get("/")
def get_public_mobils(db: Session = Depends(get_db)):
    from app.models.mobil import Mobil
    mobils = db.query(Mobil).order_by(Mobil.id.desc()).all()
    return mobils

@router.get("/test")
def test():
    return {"status": "public mobil router OK"}
