from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .admin_auth import require_admin
from database import get_db

router = APIRouter(prefix="/admin/rumah", tags=["Admin Rumah"])

@router.get("/")
def get_all_rumah(db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": "List semua rumah"}

@router.post("/")
def create_rumah(db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": "Admin nambah rumah baru"}

@router.put("/{rumah_id}")
def update_rumah(rumah_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin edit rumah {rumah_id}"}

@router.delete("/{rumah_id}")
def delete_rumah(rumah_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin hapus rumah {rumah_id}"}
