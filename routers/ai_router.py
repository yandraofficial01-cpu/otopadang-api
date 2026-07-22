from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ai import generate_deskripsi # <-- ini penting, colok ke ai.py

router = APIRouter()

# Biar datanya rapih
class DeskripsiRequest(BaseModel):
    merek: str
    tahun: int
    km: int
    harga: int

@router.post("/generate-deskripsi")
def buat_deskripsi(request: DeskripsiRequest):
    try:
        # Tembak ke fungsi di ai.py
        hasil_ai = generate_deskripsi(
            merek=request.merek,
            tahun=request.tahun,
            km=request.km,
            harga=request.harga
        )
        return {"success": True, "deskripsi": hasil_ai}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate: {str(e)}")
