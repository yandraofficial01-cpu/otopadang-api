from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List # TAMBAH INI
import models, schemas
from database import get_db
from dependencies import require_admin
from datetime import datetime
from slugify import slugify # pip install python-slugify

router = APIRouter(prefix="/blog", tags=["Blog"])

@router.get("/", response_model=List[schemas.Blog]) # TAMBAH response_model
def get_all_blog(db: Session = Depends(get_db)):
    """Public: Liat semua blog yg published"""
    blogs = db.query(models.Blog).filter(models.Blog.status == "published").order_by(models.Blog.published_at.desc()).all()
    return blogs

@router.get("/admin", response_model=List[schemas.Blog]) # TAMBAH response_model
def get_all_blog_admin(db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin: Liat semua blog termasuk draft"""
    blogs = db.query(models.Blog).order_by(models.Blog.created_at.desc()).all()
    return blogs

@router.post("/", response_model=schemas.Blog)
def create_blog(data: schemas.BlogCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin: Buat blog baru. Default draft"""
    new_slug = slugify(data.judul)
    published_at = datetime.utcnow() if data.status == "published" else None

    new_blog = models.Blog(
        **data.model_dump(),
        slug=new_slug,
        published_at=published_at
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.put("/{blog_id}/publish", response_model=schemas.Blog)
def publish_blog(blog_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin: Tombol Publish 1 klik"""
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    
    blog.status = "published"
    blog.published_at = datetime.utcnow()
    db.commit()
    db.refresh(blog)
    return blog

@router.put("/{blog_id}", response_model=schemas.Blog)
def update_blog(blog_id: int, data: schemas.BlogUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Admin: Edit blog"""
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    
    update_data = data.model_dump(exclude_unset=True)
    if "judul" in update_data: # auto update slug kalau judul ganti
        update_data["slug"] = slugify(update_data["judul"])

    for key, value in update_data.items():
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
