from fastapi import APIRouter, Depends
from app.core.deps import get_db

router = APIRouter()

@router.get("/")
def get_all_showrooms(db = Depends(get_db)):
    try:
        from app.models.showroom import Showroom
        return db.query(Showroom).all()
    except Exception as e:
        print(f"Error showroom: {e}")
        return []

@router.get("/{slug}")
def get_showroom_by_slug(slug: str, db = Depends(get_db)):
    try:
        from app.models.showroom import Showroom
        showroom = db.query(Showroom).filter(Showroom.slug == slug).first()
        if not showroom:
            return {"error": "Showroom tidak ditemukan"}
        return showroom
    except Exception as e:
        return {"error": str(e)}
