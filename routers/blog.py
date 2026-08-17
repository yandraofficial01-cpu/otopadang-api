from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from .admin_auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin Blog"])

@router.get("/blog")
def get_all_blog_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Blog).all()

@router.post("/blog")
def create_blog(data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    new_blog = models.Blog(**data); db.add(new_blog); db.commit(); db.refresh(new_blog); return new_blog

@router.put("/blog/{blog_id}")
def update_blog(blog_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    for k,v in data.items(): setattr(blog, k, v)
    db.commit(); return {"message": "Blog diupdate"}

@router.delete("/blog/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    db.delete(blog); db.commit(); return {"message": "Blog dihapus"}
