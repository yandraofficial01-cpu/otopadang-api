from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date
from enum import Enum

# ENUM
class StatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    ready = "ready"
    sold = "sold"

class PaketEnum(str, Enum):
    Basic = "Basic"
    Premium = "Premium"

class StatusBayarEnum(str, Enum):
    aktif = "aktif"
    expired = "expired"

# ========== TAMBAHAN BARU BUAT LOGIN ==========
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ========== SHOWROOM ==========
class ShowroomCreate(BaseModel):
    nama_showroom: str
    subdomain: str
    wa_number: str
    alamat: Optional[str] = None
    deskripsi: Optional[str] = None
    logo: Optional[str] = None
    email: EmailStr
    password: str

class ShowroomResponse(BaseModel):
    id: int
    nama_showroom: str
    subdomain: str
    alamat: Optional[str] = None
    deskripsi: Optional[str] = None
    logo: Optional[str] = None
    wa_number: str
    paket: PaketEnum
    status_bayar: StatusBayarEnum

    class Config:
        from_attributes = True

# ========== CAR ==========
class CarCreate(BaseModel):
    showroom_id: int
    nama_mobil: str
    merek: Optional[str] = None
    tahun: Optional[int] = None
    harga: Optional[int] = None
    harga_kredit: Optional[int] = None
    angsuran: Optional[int] = None
    lama_angsuran: Optional[int] = None
    kilometer: Optional[int] = None
    transmisi: Optional[str] = None
    bahan_bakar: Optional[str] = None
    warna: Optional[str] = None
    tipe: Optional[str] = None
    lokasi: Optional[str] = None
    deskripsi: Optional[str] = None
    foto_url_1: Optional[str] = None
    foto_url_2: Optional[str] = None
    foto_url_3: Optional[str] = None
    foto_url_4: Optional[str] = None
    foto_url_5: Optional[str] = None
    foto_url_6: Optional[str] = None
    foto_url_7: Optional[str] = None
    foto_url_8: Optional[str] = None
    video_url: Optional[str] = None
    no_wa_showroom: Optional[str] = None
    status: StatusEnum = StatusEnum.pending

class Car(CarCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
