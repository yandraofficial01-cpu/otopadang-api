from fastapi import APIRouter, Depends, Request
from app.core.deps import get_db
from app.core.subdomain import get_subdomain, get_showroom_slug

router = APIRouter()

@router.get("/")
def get_public_mobils(request: Request, db = Depends(get_db)):
    try:
        from app.models.mobil import Mobil
        from app.models.showroom import Showroom
        
        subdomain = get_subdomain(request)
        slug = get_showroom_slug(subdomain)
        
        query = db.query(Mobil)
        if slug:
            showroom = db.query(Showroom).filter(Showroom.slug == slug).first()
            if showroom:
                query = query.filter(Mobil.showroom_id == showroom.id)
        
        mobils = query.all()
        return mobils
    except Exception as e:
        print(f"Error public mobil: {e}")
        return []
