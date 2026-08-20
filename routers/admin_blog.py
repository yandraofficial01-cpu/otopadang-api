from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from routers.admin_auth import require_admin # <-- UDAH DIFIX
from database import get_db

router = APIRouter(prefix="/admin/blog", tags=["Admin Blog"])

@router.get("/")
def get_all_blog(db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": "List semua blog"}

@router.post("/")
def create_blog(db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": "Admin nambah blog baru"}

@router.put("/{blog_id}")
def update_blog(blog_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin edit blog {blog_id}"}

@router.delete("/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return {"msg": f"Admin hapus blog {blog_id}"}
