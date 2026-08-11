from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import House, LeadRumah

router = APIRouter(prefix="/rumah", tags=["Rumah"]) # TAMBAH PREFIX BIAR URL NYA /rumah

@router.get("/")
def get_all_houses(db: Session = Depends(get_db)):
    # HAPUS FILTER STATUS. Tampilkan semua data rumah, urut terbaru
    houses = db.query(House).order_by(House.created_at.desc()).all()
    return houses

@router.get("/{house_id}")
def get_house(house_id: int, db: Session = Depends(get_db)):
    house = db.query(House).filter(House.id == house_id).first()
    if not house:
        raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    return house

@router.post("/{house_id}/lead")
def create_lead(house_id: int, lead_data: dict, db: Session = Depends(get_db)):
    lead_data['house_id'] = house_id
    new_lead = LeadRumah(**lead_data)
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return {"message": "Lead berhasil dikirim", "data": new_lead}
