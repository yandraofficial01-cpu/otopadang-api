from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import models, schemas 
from database import get_db
from routers.auth_router import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def require_admin(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.showroom_id is not None:
        raise HTTPException(status_code=403, detail="Akses khusus Admin Pusat")
    return current_user

# ===============================
# 1. SHOWROOM
# ===============================
@router.get("/showrooms", response_model=list[schemas.ShowroomResponse])
def get_all_showrooms(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Showroom).all()

@router.get("/showrooms-pending", response_model=list[schemas.ShowroomResponse])
def get_showrooms_pending(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Showroom).filter(models.Showroom.status == "pending").all()

@router.post("/register-showroom", response_model=schemas.ShowroomResponse)
def register_showroom_manual(showroom: schemas.ShowroomCreate, db: Session = Depends(get_db)): # <-- PUBLIK, TANPA LOGIN
    # 1. Cek subdomain udah ada belum
    db_showroom = db.query(models.Showroom).filter(models.Showroom.subdomain == showroom.subdomain).first()
    if db_showroom:
        raise HTTPException(status_code=400, detail="Subdomain sudah dipakai")

    # 2. Cek email udah ada belum
    db_user = db.query(models.User).filter(models.User.email == showroom.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    hashed_password = hash_password(showroom.password)

    try:
        # 3. Bikin showroom dulu
        new_showroom = models.Showroom(
            nama_showroom=showroom.nama_showroom,
            subdomain=showroom.subdomain,
            wa_number=showroom.wa_number,
            alamat=showroom.alamat,
            deskripsi=showroom.deskripsi,
            logo=showroom.logo,
            status="pending", # Biar di approve admin dulu
            status_bayar="trial",
            paket="Free"
        )
        db.add(new_showroom)
        db.commit()
        db.refresh(new_showroom)

        # 4. Bikin user admin showroom nya
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
        db.rollback() # <-- PENTING: kalau gagal, hapus semua
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
# 2. MOBIL
# ===============================
@router.get("/mobil", response_model=list[schemas.MobilResponse])
def get_all_mobil_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Car).all()

@router.put("/mobil/{mobil_id}")
def update_mobil_status(mobil_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil: raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    for key, value in data.items():
        setattr(mobil, key, value)
    db.commit()
    return {"message": f"Status mobil {mobil_id} diupdate"}

# ===============================
# 3. RUMAH - FIX DOBEL ROUTE BIAR FE LAMA & BARU JALAN
# ===============================
@router.get("/rumah", response_model=list[schemas.RumahResponse])
def get_all_rumah_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
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
    rumah = db.query(models.House).filter(models.House.id == rumah_id).first()
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    for key, value in data.items():
        setattr(rumah, key, value)
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
# 4. BLOG
# ===============================
@router.get("/blog")
def get_all_blog_admin(db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    return db.query(models.Blog).all()

@router.post("/blog")
def create_blog(data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    new_blog = models.Blog(**data)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.put("/blog/{blog_id}")
def update_blog(blog_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    for k,v in data.items():
        setattr(blog, k, v)
    db.commit()
    return {"message": "Blog diupdate"}

@router.delete("/blog/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog: raise HTTPException(status_code=404, detail="Blog tidak ditemukan")
    db.delete(blog)
    db.commit()
    return {"message": "Blog dihapus"}
