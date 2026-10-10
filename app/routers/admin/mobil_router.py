from fastapi import APIRouter, Depends
from app.core.deps import get_db, get_current_admin

router = APIRouter()

@router.get("/")
def list_mobil(db = Depends(get_db), admin = Depends(get_current_admin)):
    return []

@router.post("/")
def create_mobil(data: dict, db = Depends(get_db), admin = Depends(get_current_admin)):
    return {"message": "mobil created"}
