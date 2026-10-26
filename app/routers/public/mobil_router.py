from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.deps import get_db

router = APIRouter()

@router.get("/")
def get_public_mobils(request: Request, db: Session = Depends(get_db)):
    from app.models.mobil import Mobil
    from app.models.showroom import Showroom

    # Ambil host tanpa try-except yang nutupin error
    host = request.headers.get("host", "")
    slug = None

    # Deteksi subdomain agung.otopadang.com -> agung
    if "otopadang" in host:
        parts = host.split(".")
        if len(parts) >= 3:  # agung.otopadang.com
            potential_slug = parts[0]
            if potential_slug not in ["www", "api"]:
                slug = potential_slug

    query = db.query(Mobil)

    # Kalau ada slug (agung) -> filter, kalau gak ada (otopadang.com) -> semua
    if slug:
        showroom = db.query(Showroom).filter(Showroom.slug == slug).first()
        if showroom:
            query = query.filter(Mobil.showroom_id == showroom.id)

    mobils = query.order_by(Mobil.id.desc()).all()
    
    # Convert manual biar pasti ke-JSON, gak error serialization
    data = []
    for m in mobils:
        data.append({
            "id": m.id,
            "merek": getattr(m, 'merek', ''),
            "nama_mobil": getattr(m, 'nama_mobil', '') or getattr(m, 'nama', ''),
            "harga": getattr(m, 'harga', 0),
            "tahun": getattr(m, 'tahun', 0),
            "kilometer": getattr(m, 'kilometer', 0),
            "gambar": getattr(m, 'gambar', None) or getattr(m, 'images', []),
            "showroom_id": getattr(m, 'showroom_id', None),
        })
    return data
