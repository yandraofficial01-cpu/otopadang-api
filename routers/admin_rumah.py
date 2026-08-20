from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import cloudinary
import cloudinary.uploader
from database import get_db
from models import Rumah # GANTI DARI House -> Rumah
from.admin_auth import require_admin

router = APIRouter(tags=["Admin Rumah"]) # HAPUS PREFIX DISINI

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

class RumahCreate(BaseModel):
    nama_rumah: str
    tipe: Optional[str] = None
    alamat: Optional[str] = None
    harga: Optional[int] = None
    harga_kredit: Optional[int] = None
    angsuran: Optional[int] = None
    lama_angsuran: Optional[int] = 120
    luas_tanah: Optional[int] = None
    luas_bangunan: Optional[int] = None
    spesifikasi: Optional[str] = None
    badge_bonus: Optional[str] = "Free Canopy"
    foto_url_1: Optional[str] = None
    foto_url_2: Optional[str] = None
    foto_url_3: Optional[str] = None
    foto_url_4: Optional[str] = None
    foto_url_5: Optional[str] = None
    foto_url_6: Optional[str] = None
    foto_url_7: Optional[str] = None
    foto_url_8: Optional[str] = None
    video_url: Optional[str] = None
    wa_number: Optional[str] = "628979879518"
    status: str = "available"

class RumahUpdate(BaseModel):
    nama_rumah: Optional[str] = None
    tipe: Optional[str] = None
    alamat: Optional[str] = None
    harga: Optional[int] = None
    harga_kredit: Optional[int] = None
    angsuran: Optional[int] = None
    lama_angsuran: Optional[int] = None
    luas_tanah: Optional[int] = None
    luas_bangunan: Optional[int] = None
    spesifikasi: Optional[str] = None
    badge_bonus: Optional[str] = None
    status: Optional[str] = None
    wa_number: Optional[str] = None
    foto_url_1: Optional[str] = None
    foto_url_2: Optional[str] = None
    foto_url_3: Optional[str] = None
    foto_url_4: Optional[str] = None
    foto_url_5: Optional[str] = None
    foto_url_6: Optional[str] = None
    foto_url_7: Optional[str] = None
    foto_url_8: Optional[str] = None
    video_url: Optional[str] = None

@router.post("/upload")
async def upload_rumah_foto(file: UploadFile = File(...), admin = Depends(require_admin)):
    try:
        result = cloudinary.uploader.upload(file.file, upload_preset="otopadang_preset", folder="otopadang/rumah")
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload gagal: {str(e)}")

@router.get("/")
def get_all_rumah_admin(db: Session = Depends(get_db), admin = Depends(require_admin)):
    rumah_list = db.query(Rumah).order_by(Rumah.id.desc()).all() # GANTI House -> Rumah
    return [{
        "id": r.id, "nama_rumah": r.nama_rumah, "tipe": r.tipe, "alamat": r.alamat,
        "harga": r.harga, "harga_kredit": r.harga_kredit, "angsuran": r.angsuran,
        "lama_angsuran": r.lama_angsuran, "luas_tanah": r.luas_tanah, "luas_bangunan": r.luas_bangunan,
        "spesifikasi": r.spesifikasi, "badge_bonus": r.badge_bonus,
        "foto_url_1": r.foto_url_1, "foto_url_2": r.foto_url_2, "foto_url_3": r.foto_url_3, "foto_url_4": r.foto_url_4,
        "foto_url_5": r.foto_url_5, "foto_url_6": r.foto_url_6, "foto_url_7": r.foto_url_7, "foto_url_8": r.foto_url_8,
        "video_url": r.video_url, "wa_number": r.wa_number, "status": r.status, "created_at": r.created_at
    } for r in rumah_list]

@router.post("/")
def create_rumah(data: RumahCreate, db: Session = Depends(get_db), admin = Depends(require_admin)):
    new_rumah = Rumah(**data.dict()) # GANTI House -> Rumah
    db.add(new_rumah)
    db.commit()
    db.refresh(new_rumah)
    return {"message": "Rumah berhasil ditambahkan", "id": new_rumah.id}

@router.put("/{rumah_id}")
def update_rumah(rumah_id: int, data: RumahUpdate, db: Session = Depends(get_db), admin = Depends(require_admin)):
    rumah = db.query(Rumah).filter(Rumah.id == rumah_id).first() # GANTI House -> Rumah
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    for key, value in data.dict(exclude_unset=True).items(): setattr(rumah, key, value)
    db.commit()
    db.refresh(rumah)
    return {"message": "Rumah berhasil diupdate"}

@router.delete("/{rumah_id}")
def delete_rumah(rumah_id: int, db: Session = Depends(get_db), admin = Depends(require_admin)):
    rumah = db.query(Rumah).filter(Rumah.id == rumah_id).first() # GANTI House -> Rumah
    if not rumah: raise HTTPException(status_code=404, detail="Rumah tidak ditemukan")
    db.delete(rumah)
    db.commit()
    return {"message": "Rumah berhasil dihapus"}
