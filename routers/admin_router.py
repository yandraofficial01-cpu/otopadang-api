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
    # FIX: Cek role biar aman
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Akses khusus Admin Pusat")
    return current_user

# ===============================
# 0. DASHBOARD STATS
# ===============================
@router.get("/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    total_mobil = db.query(models.Car).count()
    mobil_pending = db.query(models.Car).filter(models.Car.status == "pending").count()
    total_showroom = db.query(models.Showroom).count()
    total_rumah = db.query(models.House).count()
    total_blog = db.query(models.Blog).count()
    
    return {
        "total_mobil": total_mobil,
        "mobil_pending": mobil_pending,
        "total_showroom": total_showroom,
        "total_rumah": total_rumah,
        "total_blog": total_blog
    }

# ===============================
# 1. SHOWROOM
# ===============================
@router.get("/showrooms", response_model=List[schemas.ShowroomResponse])
def get_all_showrooms(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Showroom).all()

@router.get("/showrooms-pending", response_model=List[schemas.ShowroomResponse])
def get_showrooms_pending(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Showroom).filter(models.Showroom.status == "pending").all()

@router.post("/register-showroom", response_model=schemas.ShowroomResponse)
def register_showroom_manual(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db)):
    db_showroom = db.query(models.Showroom).filter(models.Showroom.subdomain == showroom.subdomain).first()
    if db_showroom:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")

    db_user = db.query(models.User).filter(models.User.email == showroom.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    hashed_password = hash_password(showroom.password)

    try:
        new_showroom = models.Showroom(
            nama_showroom=showroom.nama_showroom,
            subdomain=showroom.subdomain,
            wa_number=showroom.wa_number,
            alamat=showroom.alamat,
            deskripsi=showroom.deskripsi,
            logo=showroom.logo,
            status="pending",
            status_bayar="trial",
            paket="Free"
        )
        db.add(new_showroom)
        db.commit()
        db.refresh(new_showroom)

        new_user = models.User(
            showroom_id=new_showroom.id,
            email=showroom.email,
            password=hashed_password,
            name=showroom.nama_showroom,
            role='showroom',
            status='active'
        )
        db.add(new_user)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal daftar: {str(e)}")

    return new_showroom

@router.put("/showrooms/{showroom_id}/approve")
def approve_showroom(showroom_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.status = "approved"
    showroom.status_bayar = "aktif"
    db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} berhasil di approve"}

@router.put("/showrooms/{showroom_id}/premium")
def set_premium(showroom_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    showroom = db.query(models.Showroom).filter(models.Showroom.id == showroom_id).first()
    if not showroom: raise HTTPException(status_code=404, detail="Showroom tidak ditemukan")
    showroom.paket = "Premium"
    showroom.status_bayar = "aktif"
    db.commit()
    return {"message": f"Showroom {showroom.nama_showroom} jadi Premium"}

# ===============================
# 2. MOBIL - FIX: TAMPILKAN SEMUA TERMASUK SOLDOUT
# ===============================
@router.get("/mobil", response_model=List[schemas.MobilResponse])
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # FIX: AMBIL SEMUA STATUS. JANGAN FILTER. Biar soldout tetap tampil
    results = db.query(models.Car, models.User.name.label("showroom_nama")) \
        .outerjoin(models.User, models.Car.showroom_id == models.User.showroom_id) \
        .order_by(models.Car.id.desc()).all()

    mobil_list = []
    for car, showroom_nama in results:
        mobil_dict = schemas.MobilResponse.model_validate(car).model_dump()
        mobil_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
        mobil_list.append(mobil_dict)
    
    return mobil_list

@router.get("/mobil-pending", response_model=List[schemas.MobilResponse])
def get_mobil_pending_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    results = db.query(models.Car, models.User.name.label("showroom_nama")) \
        .outerjoin(models.User, models.Car.showroom_id == models.User.showroom_id) \
        .filter(models.Car.status == 'pending') \
        .order_by(models.Car.id.desc()).all()

    mobil_list = []
    for car, showroom_nama in results:
        mobil_dict = schemas.MobilResponse.model_validate(car).model_dump()
        mobil_dict['showroom_nama'] = showroom_nama or "Admin Pusat"
        mobil_list.append(mobil_dict)
    
    return mobil_list

@router.put("/mobil/{mobil_id}")
def update_mobil_status(mobil_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    for key, value in data.items():
        setattr(mobil, key, value)
    db.commit()
    return {"message": f"Status mobil {mobil_id} diupdate"}

@router.delete("/mobil/{mobil_id}")
def delete_mobil(mobil_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    db.delete(mobil)
    db.commit()
    return {"message": "Mobil dihapus"}

# ===============================
# 3. RUMAH - FIX: BISA SOLDOUT & BISA DELETE
# ===============================
@router.get("/rumah", response_model=List[schemas.RumahResponse])
def get_all_rumah_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # FIX: AMBIL SEMUA. Biar yg status='terjual' tetap tampil
    return db.query(models.House).order_by(models.House.id.desc()).all()

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
    # FIX: Bisa update status jadi 'terjual'
    rumah = db.query(models.House).filter(models.House.id == rumah_id).first()
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    for key, value in data.items():
        setattr(rumah, key, value)
    db.commit()
    return {"message": f"Status rumah diupdate"}

@router.delete("/rumah/{rumah_id}")
def delete_rumah(rumah_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    # FIX: INI YG KEMARIN BELUM ADA
    rumah = db.query(models.House).filter(models.House.id == rumah_id).first()
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    db.delete(rumah)
    db.commit()
    return {"message": "Rumah dihapus"}

# ===============================
# 4. BLOG - FIX: ANTI ERROR 500
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
