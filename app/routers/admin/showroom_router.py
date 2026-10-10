from fastapi import APIRouter, Depends
from app.core.deps import get_db, get_current_admin

router = APIRouter()

@router.get("/")
def list_showroom(db = Depends(get_db), admin = Depends(get_current_admin)):
    return {"message": "showroom admin ok"}

@router.post("/")
def create_showroom(data: dict, db = Depends(get_db), admin = Depends(get_current_admin)):
    return {"message": "created", "data": data}
