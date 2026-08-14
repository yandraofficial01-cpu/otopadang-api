from sqlalchemy import Column, Integer, String, BigInteger, Text, DECIMAL, Date, TIMESTAMP, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Showroom(Base):
    __tablename__ = "showrooms"
    id = Column(Integer, primary_key=True, index=True)
    nama_showroom = Column(String(100), nullable=False)
    subdomain = Column(String(50), unique=True, nullable=False, index=True)
    alamat = Column(Text)
    deskripsi = Column(Text)
    logo = Column(String(255))
    wa_number = Column(String(20), nullable=False)
    paket = Column(String(50), default='Free')
    status_bayar = Column(String(50), default='trial')
    status = Column(String(50), default='pending', nullable=False, index=True)
    tgl_expired = Column(Date)
    created_at = Column(TIMESTAMP, server_default=func.now())

    cars = relationship("Car", back_populates="showroom", cascade="all, delete-orphan")
    users = relationship("User", back_populates="showroom", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), default='showroom', index=True) # admin, showroom
    status = Column(String(50), default='active')
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    showroom = relationship("Showroom", back_populates="users")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id", ondelete="CASCADE"), index=True)
    nama_mobil = Column(String(100), nullable=False, index=True)
    merek = Column(String(50), index=True)
    tahun = Column(Integer, index=True)
    harga = Column(BigInteger)
    harga_kredit = Column(BigInteger)
    angsuran = Column(BigInteger)
    lama_angsuran = Column(Integer)
    kilometer = Column(Integer)
    transmisi = Column(String(20))
    bahan_bakar = Column(String(20))
    warna = Column(String(30))
    tipe = Column(String(50))
    lokasi = Column(String(255))
    deskripsi = Column(Text)
    foto_url_1 = Column(String(255))
    foto_url_2 = Column(String(255))
    foto_url_3 = Column(String(255))
    foto_url_4 = Column(String(255))
    foto_url_5 = Column(String(255))
    foto_url_6 = Column(String(255))
    foto_url_7 = Column(String(255))
    foto_url_8 = Column(String(255))
    video_url = Column(String(255))
    no_wa_showroom = Column(String(20))
    status = Column(String(50), default='pending', index=True) # pending, approved, rejected, sold
    sold_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    showroom = relationship("Showroom", back_populates="cars")

class House(Base):
    __tablename__ = "rumah"
    id = Column(Integer, primary_key=True, index=True)
    nama_rumah = Column(String(100), nullable=False, index=True)
    tipe = Column(String(50))
    alamat = Column(Text)
    harga = Column(BigInteger, nullable=False)
    harga_kredit = Column(BigInteger, default=0)
    angsuran = Column(BigInteger, default=0)
    lama_angsuran = Column(Integer, default=120)
    luas_tanah = Column(Integer, default=0)
    luas_bangunan = Column(Integer, default=0)
    spesifikasi = Column(Text)
    badge_bonus = Column(String(50), default='Free Canopy')
    foto_url_1 = Column(String(255))
    foto_url_2 = Column(String(255))
    foto_url_3 = Column(String(255))
    foto_url_4 = Column(String(255))
    foto_url_5 = Column(String(255))
    foto_url_6 = Column(String(255))
    foto_url_7 = Column(String(255))
    foto_url_8 = Column(String(255))
    video_url = Column(String(255))
    wa_number = Column(String(20), default='628979879518')
    status = Column(String(50), default='available', index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False) # URL SEO
    konten = Column(Text) # Isi artikel HTML
    gambar_cover = Column(String(255)) # Gambar utama
    penulis = Column(String(100), default='Admin Otopadang')
    kategori = Column(String(50), default='Tips', index=True) # Review, Berita, Tips KPR, Edukasi
    tags = Column(String(255)) # pisah koma: mobil bekas, avanza, padang
    meta_description = Column(String(160)) # Deskripsi SEO 160 karakter

    # FITUR IKLAN / ENDORSE
    is_sponsored = Column(Boolean, default=False, index=True) # True kalau artikel sponsor
    nama_pengiklan = Column(String(100), nullable=True) # Nama Showroom yg bayar
    link_pengiklan = Column(String(255), nullable=True) # Link WA/IG pengiklan

    status = Column(String(50), default='draft', index=True) # draft, publish, scheduled
    published_at = Column(TIMESTAMP, nullable=True, index=True) # Tanggal tayang. Wajib buat Google News
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now()) # Auto update

class LeadRumah(Base):
    __tablename__ = "leads_rumah"
    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("rumah.id", ondelete="CASCADE"), index=True)
    nama_buyer = Column(String(100))
    no_wa_buyer = Column(String(20))
    status = Column(String(50), default='Tanya', index=True) # Tanya, Survey, Deal
    fee_persen = Column(DECIMAL(4,2), default=2.00)
    nilai_fee = Column(BigInteger)
    tgl_akad = Column(Date)
    catatan = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    house = relationship("House")
