from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Rumah

router = APIRouter(prefix="/rumah", tags=["Rumah Publik"])

@router.get("/all-public")
def get_all_rumah_public(db: Session = Depends(get_db)):
    rumah_list = db.query(Rumah).filter(Rumah.status == "available").order_by(Rumah.id.desc()).all()
    return [{
        "id": r.id, "nama_rumah": r.nama_rumah, "tipe": r.tipe, "alamat": r.alamat,
        "harga": r.harga, "harga_kredit": r.harga_kredit, "angsuran": r.angsuran,
        "lama_angsuran": r.lama_angsuran, "luas_tanah": r.luas_tanah, "luas_bangunan": r.luas_bangunan,
        "spesifikasi": r.spesifikasi, "badge_bonus": r.badge_bonus,
        "foto_url_1": r.foto_url_1, "foto_url_2": r.foto_url_2, "foto_url_3": r.foto_url_3, "foto_url_4": r.foto_url_4,
        "foto_url_5": r.foto_url_5, "foto_url_6": r.foto_url_6, "foto_url_7": r.foto_url_7, "foto_url_8": r.foto_url_8,
        "video_url": r.video_url, "wa_number": r.wa_number, "status": r.status, "created_at": r.created_at
    } for r in rumah_list]
