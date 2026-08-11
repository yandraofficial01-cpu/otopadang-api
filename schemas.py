from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum

# ENUM
class StatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    ready = "ready"
    sold = "sold"

class ShowroomStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class PaketEnum(str, Enum):
    Basic = "Basic"
    Premium = "Premium"

class StatusBayarEnum(str, Enum):
    aktif = "aktif"
    expired = "expired"

class HouseStatusEnum(str, Enum):
    available = "available"
    sold = "sold"

class LeadRumahStatusEnum(str, Enum):
    Tanya = "Tanya"
    Survey = "Survey"
    Booking = "Booking"
    Akad = "Akad"
    Gagal = "Gagal"

class BlogStatusEnum(str, Enum):
    draft = "draft"
    publish = "publish"

# ========== AUTH ==========
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterShowroomRequest(BaseModel):
    nama_showroom: str = Field(..., min_length=3)
    subdomain: str = Field(..., min_length=3, pattern="^[a-z0-9-]+$")
    alamat: Optional[str] = None
    wa_number: str
    email: EmailStr
    password: str = Field(..., min_length=6)

# ========== SHOWROOM ==========
class ShowroomCreate(BaseModel):
    """Khusus admin yg daftarin manual"""
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
    status: ShowroomStatusEnum

    class Config:
        from_attributes = True

class ShowroomUpdate(BaseModel):
    nama_showroom: Optional[str] = None
    alamat: Optional[str] = None
    deskripsi: Optional[str] = None
    logo: Optional[str] = None
    wa_number: Optional[str] = None

# ========== MOBIL / CAR ==========
class CarCreate(BaseModel):
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

class CarResponse(CarCreate):
    id: int
    showroom_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ALIAS BIAR GA GANTI ADMIN_ROUTER
MobilCreate = CarCreate
MobilResponse = CarResponse

# ========== RUMAH / HOUSE - FIX INI DOANG ==========
class RumahCreate(BaseModel):
    nama_rumah: str # wajib
    tipe: Optional[str] = None
    alamat: Optional[str] = None
    harga: int # wajib
    harga_kredit: Optional[int] = 0
    angsuran: Optional[int] = 0
    lama_angsuran: Optional[int] = 120
    luas_tanah: Optional[int] = 0
    luas_bangunan: Optional[int] = 0
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
    status: HouseStatusEnum = HouseStatusEnum.available

class RumahResponse(RumahCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ALIAS KOMPATIBEL UNTUK ROUTER BARU & LAMA
HouseCreate = RumahCreate
HouseResponse = RumahResponse
RumahBase = RumahCreate

# ========== BLOG ==========
class BlogBase(BaseModel):
    judul: str
    slug: str
    konten: str
    gambar: Optional[str] = None
    penulis: Optional[str] = "Admin"
    status: BlogStatusEnum = BlogStatusEnum.publish

class BlogCreate(BlogBase):
    pass

class BlogResponse(BlogBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# ========== LEAD RUMAH ==========
class LeadRumahCreate(BaseModel):
    house_id: int
    nama_buyer: str
    no_wa_buyer: str
    status: LeadRumahStatusEnum = LeadRumahStatusEnum.Tanya
    fee_persen: Optional[float] = 2.00
    nilai_fee: Optional[int] = None
    tgl_akad: Optional[date] = None
    catatan: Optional[str] = None

class LeadRumahResponse(LeadRumahCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
