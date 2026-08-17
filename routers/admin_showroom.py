from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .admin_auth import require_admin
from database import get_db

router = APIRouter(prefix="/admin/showroom", tags=["Admin Showroom"])

@router.get("/")
def get_all_showroom(db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": "List semua showroom"}

@router.put("/{showroom_id}/verify")
def verify_showroom(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin verifikasi showroom {showroom_id}"}

@router.delete("/{showroom_id}")
def delete_showroom(showroom_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin hapus showroom {showroom_id}"}
