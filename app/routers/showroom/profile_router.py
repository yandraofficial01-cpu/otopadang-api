from fastapi import APIRouter, Depends
from app.core.deps import get_db

router = APIRouter()

@router.get("/")
def get_my_profile(db = Depends(get_db)):
    # nanti kita pasang auth showroom
    return {"message": "profile showroom", "slug": "agung"}

@router.put("/")
def update_profile(data: dict, db = Depends(get_db)):
    return {"message": "profile updated", "data": data}
