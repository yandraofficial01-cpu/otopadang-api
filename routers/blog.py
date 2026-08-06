from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from dependencies import require_admin
from datetime import datetime

router = APIRouter(prefix="/blog", tags=["Blog"]) # <-- INI KUNCINYA

@router.get("/")
def get_all_blog(db: Session = Depends(get_db)):
    """Public: Liat semua blog yg approved"""
    blogs = db.query(models.Blog).filter(models.Blog.status == "approved").order_by(models.Blog.created_at.desc()).all()
    return blogs

@router.get("/admin")
def get_all_blog_admin(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin: Liat semua blog termasuk draft"""
    blogs = db.query(models.Blog).order_by(models.Blog.created_at.desc()).all()
    return blogs

@router.post("/")
def create_blog(data: schemas.BlogCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin: Buat blog baru langsung tayang"""
    new_blog = models.Blog(**data.model_dump(), status="approved", created_at=datetime.utcnow())
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.put("/{blog_id}")
def update_blog(blog_id: int, data: dict, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin: Edit / Approve / Reject blog"""
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    for key, value in data.items():
        setattr(blog, key, value)
    db.commit()
    db.refresh(blog)
    return blog

@router.delete("/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin: Hapus blog"""
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    db.delete(blog)
    db.commit()
    return {"message": "Blog berhasil dihapus"}
