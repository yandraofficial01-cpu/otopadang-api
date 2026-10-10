from fastapi import APIRouter, Depends
from app.core.deps import get_db

router = APIRouter()

@router.get("/")
def get_my_mobils(db = Depends(get_db)):
    try:
        from app.models.mobil import Mobil
        # untuk sekarang return semua dulu
        return db.query(Mobil).all()
    except:
        return []

@router.post("/")
def create_my_mobil(data: dict, db = Depends(get_db)):
    try:
        from app.models.mobil import Mobil
        mobil = Mobil(**data)
        db.add(mobil)
        db.commit()
        db.refresh(mobil)
        return mobil
    except Exception as e:
        return {"error": str(e)}

@router.delete("/{mobil_id}")
def delete_my_mobil(mobil_id: int, db = Depends(get_db)):
    try:
        from app.models.mobil import Mobil
        mobil = db.query(Mobil).filter(Mobil.id == mobil_id).first()
        if mobil:
            db.delete(mobil)
            db.commit()
            return {"message": "deleted"}
        return {"error": "not found"}
    except Exception as e:
        return {"error": str(e)}
