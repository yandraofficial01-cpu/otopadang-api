from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import bcrypt
import models, schemas 
from database import get_db
from routers.auth_router import get_current_user
from datetime import datetime
from slugify import slugify

router = APIRouter(prefix="/admin", tags=["Admin"])

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def require_admin(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # FIX: Cek role biar gak ketergantungan showroom_id
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Akses khusus Admin Pusat")
    return current_user

# ===============================
# 1. SHOWROOM - UDAH OKE
# ===============================
@router.get("/showrooms", response_model=List[schemas.ShowroomResponse])
def get_all_showrooms(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Showroom).all()

@router.get("/showrooms-pending", response_model=List[schemas.ShowroomResponse])
def get_showrooms_pending(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Showroom).filter(models.Showroom.status == "pending").all()

@router.post("/register-showroom", response_model=schemas.ShowroomResponse)
def register_showroom_manual(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db)):
    # ... kode lu udah bener, biarin
    pass

@router.put("/showrooms/{showroom_id}/approve")
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # ... kode lu udah bener
    pass

@router.put("/showrooms/{showroom_id}/premium")
def set_premium(showroom_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # ... kode lu udah bener
    pass

# ===============================
# 2. MOBIL - UDAH SESUAI PERMINTAAN
# ===============================
@router.get("/mobil", response_model=List[schemas.MobilResponse])
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    results = db.query(models.Car, models.User.name.label("showroom_nama")) \
        .outerjoin(models.User, models.Car.showroom_id == models.User.showroom_id) \
        .order_by(models.Car.id.desc()).all() # AMBIL SEMUA TERMASUK SOLDOUT

    mobil_list = []
    for car, showroom_nama in results:
        mobil_dict = schemas.MobilResponse.model_validate(car).model_dump()
        mobil_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
        mobil_list.append(mobil_dict)
    
    return mobil_list

@router.get("/mobil-pending", response_model=List[schemas.MobilResponse])
def get_mobil_pending_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # ... kode lu udah bener
    pass

@router.put("/mobil/{mobil_id}")
def update_mobil_status(mobil_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    for key, value in data.items():
        setattr(mobil, key, value) # Bisa set status: "soldout"
    db.commit()
    return {"message": f"Status mobil {mobil_id} diupdate"}

@router.delete("/mobil/{mobil_id}")
def delete_mobil(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # ... kode lu udah bener
    pass

# ===============================
# 3. RUMAH - UDAH SESUAI PERMINTAAN
# ===============================
@router.get("/rumah", response_model=List[schemas.RumahResponse])
def get_all_rumah_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.House).order_by(models.House.id.desc()).all() # AMBIL SEMUA TERMASUK TERJUAL

@router.post("/rumah", response_model=schemas.RumahResponse)
@router.post("/upload-rumah", response_model=schemas.RumahResponse)
def upload_rumah(data: schemas.RumahCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    new_rumah = models.House(**data.model_dump())
    db.add(new_rumah)
    db.commit()
    db.refresh(new_rumah)
    return new_rumah

@router.put("/rumah/{rumah_id}")
def update_rumah_status(rumah_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    rumah = db.query(models.House).filter(models.House.id == rumah_id).first()
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    for key, value in data.items():
        setattr(rumah, key, value) # Bisa set status: "terjual"
    db.commit()
    return {"message": f"Status rumah diupdate"}

@router.delete("/rumah/{rumah_id}")
def delete_rumah(rumah_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    rumah = db.query(models.House).filter(models.House.id == rumah_id).first()
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    db.delete(rumah)
    db.commit()
    return {"message": "Rumah dihapus"}

# ===============================
# 4. BLOG - UDAH FIX ANTI 500
# ===============================
@router.get("/blog", response_model=List[schemas.BlogResponse])
def get_all_blog_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Blog).order_by(models.Blog.created_at.desc().nullslast()).all()

@router.post("/blog", response_model=schemas.BlogResponse)
def create_blog(data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    new_blog = models.Blog(
        **data,
        slug=slugify(data.get("judul")),
        created_at=datetime.utcnow(),
        penulis=current_user.name or "Admin"
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.put("/blog/{blog_id}/publish", response_model=schemas.BlogResponse)
def publish_blog(blog_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    blog.status = "published"
    blog.published_at = datetime.utcnow()
    db.commit()
    db.refresh(blog)
    return blog

@router.put("/blog/{blog_id}", response_model=schemas.BlogResponse)
def update_blog(blog_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    if "judul" in data:
        data["slug"] = slugify(data["judul"])
    for k,v in data.items():
        setattr(blog, k, v)
    db.commit()
    db.refresh(blog)
    return blog

@router.delete("/blog/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    db.delete(blog)
    db.commit()
    return {"message": "Blog dihapus"}
