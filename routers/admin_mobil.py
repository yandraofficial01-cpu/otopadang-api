from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .admin_auth import require_admin
from database import get_db

router = APIRouter(prefix="/admin/mobil", tags=["Admin Mobil"])

@router.get("/")
def get_all_cars(db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": "Admin liat semua mobil"}

@router.put("/{mobil_id}/approve")
def approve_car(mobil_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin approve mobil {mobil_id}"}

@router.put("/{mobil_id}/soldout")
def soldout_car(mobil_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin soldout mobil {mobil_id}"}

@router.delete("/{mobil_id}")
def delete_car(mobil_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin delete mobil {mobil_id}"}
