from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date

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
    paket: str
    status_bayar: str
    status: str
    created_at: Optional[datetime] = None # <--- TAMBAH BIAR AMAN
    class Config:
        from_attributes = True

# ========== MOBIL / CAR ==========
class CarCreate(BaseModel):
    nama_mobil: str
    merek: str
    tahun: Optional[int] = None
    harga: int
    harga_kredit: Optional[int] = None
    angsuran: Optional[int] = None
    lama_angsuran: Optional[int] = None
    kilometer: Optional[int] = None
    transmisi: Optional[str] = "Manual"
    bahan_bakar: Optional[str] = "Bensin"
    warna: Optional[str] = None
    tipe: Optional[str] = None
    lokasi: Optional[str] = None
    deskripsi: Optional[str] = None
    spesifikasi: Optional[str] = None
    foto_url_1: str
    foto_url_2: Optional[str] = None
    foto_url_3: Optional[str] = None
    foto_url_4: Optional[str] = None
    foto_url_5: Optional[str] = None
    foto_url_6: Optional[str] = None
    foto_url_7: Optional[str] = None
    foto_url_8: Optional[str] = None
    video_url: Optional[str] = None
    no_wa_showroom: Optional[str] = None

class MobilUpdate(BaseModel):
    harga: Optional[int] = None
    no_wa_showroom: Optional[str] = None
    deskripsi: Optional[str] = None
    spesifikasi: Optional[str] = None
    class Config:
        extra = "forbid"

class CarResponse(BaseModel):
    id: int
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
    spesifikasi: Optional[str] = None
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
    status: str
    status_jual: Optional[str] = None
    sold_at: Optional[datetime] = None
    created_at: Optional[datetime] = None # <--- INI YG DIGANTI. KASIH OPTIONAL
    showroom_nama: Optional[str] = None

    class Config:
        from_attributes = True

MobilCreate = CarCreate
MobilResponse = CarResponse

# ========== RUMAH / HOUSE ==========
class RumahCreate(BaseModel):
    nama_rumah: str
    tipe: Optional[str] = None
    alamat: Optional[str] = None
    harga: int
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
    status: str = "available"

class RumahResponse(RumahCreate):
    id: int
    created_at: Optional[datetime] = None # <--- KASIH OPTIONAL JUGA
    class Config:
        from_attributes = True

HouseCreate = RumahCreate
HouseResponse = RumahResponse
RumahBase = RumahCreate

# ========== BLOG ==========
class BlogBase(BaseModel):
    judul: str
    konten: str
    gambar_cover: Optional[str] = None
    penulis: str
    kategori: str = "Tips"
    tags: Optional[str] = None
    meta_description: Optional[str] = None
    is_sponsored: bool = False
    nama_pengiklan: Optional[str] = None
    link_pengiklan: Optional[str] = None
    status: str = "draft"

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BaseModel):
    judul: Optional[str] = None
    konten: Optional[str] = None
    gambar_cover: Optional[str] = None
    penulis: Optional[str] = None
    kategori: Optional[str] = None
    tags: Optional[str] = None
    meta_description: Optional[str] = None
    is_sponsored: Optional[bool] = None
    nama_pengiklan: Optional[str] = None
    link_pengiklan: Optional[str] = None
    status: Optional[str] = None

class BlogResponse(BlogBase):
    id: int
    slug: str
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None # <--- KASIH OPTIONAL JUGA
    updated_at: Optional[datetime] = None # <--- KASIH OPTIONAL JUGA
    class Config:
        from_attributes = True

# ========== LEAD RUMAH ==========
class LeadRumahCreate(BaseModel):
    house_id: int
    nama_buyer: str
    no_wa_buyer: str
    status: str = "Tanya"
    fee_persen: Optional[float] = 2.00
    nilai_fee: Optional[int] = None
    tgl_akad: Optional[date] = None
    catatan: Optional[str] = None

class LeadRumahResponse(LeadRumahCreate):
    id: int
    created_at: Optional[datetime] = None # <--- KASIH OPTIONAL JUGA
    class Config:
        from_attributes = True
