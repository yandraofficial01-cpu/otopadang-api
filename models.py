from sqlalchemy import Column, Integer, String, BigInteger, Text, Enum, DECIMAL, Date, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Showroom(Base):
    __tablename__ = "showrooms"
    id = Column(Integer, primary_key=True, index=True)
    nama_showroom = Column(String(100), nullable=False)
    subdomain = Column(String(50), unique=True, nullable=False)
    alamat = Column(Text)
    deskripsi = Column(Text)
    logo = Column(String(255))
    wa_number = Column(String(20), nullable=False)
    paket = Column(Enum('Basic', 'Premium', name='paket_enum'), default='Basic')
    status_bayar = Column(Enum('aktif', 'expired', name='status_bayar_enum'), default='aktif')
    status = Column(Enum('pending', 'approved', 'rejected', name='showroom_status_enum'), default='pending', nullable=False)
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
    role = Column(String(50), default='showroom')
    status = Column(String(50), default='active')
    created_at = Column(TIMESTAMP, server_default=func.now())
    showroom = relationship("Showroom", back_populates="users")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id", ondelete="CASCADE"))
    nama_mobil = Column(String(100))
    merek = Column(String(50))
    tahun = Column(Integer)
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
    status = Column(Enum('pending', 'approved', 'ready', 'sold', name='car_status_enum'), default='pending')
    created_at = Column(TIMESTAMP, server_default=func.now())
    showroom = relationship("Showroom", back_populates="cars")

class House(Base):
    __tablename__ = "rumah" # INI DOANG YG GUE GANTI
    id = Column(Integer, primary_key=True, index=True)
    nama_rumah = Column(String(100), nullable=False)
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
    status = Column(Enum('available', 'sold', name='house_status_enum'), default='available')
    created_at = Column(TIMESTAMP, server_default=func.now())

class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True)
    konten = Column(Text)
    gambar = Column(String(255))
    penulis = Column(String(100), default='Admin')
    status = Column(Enum('draft', 'publish', name='blog_status_enum'), default='publish')
    created_at = Column(TIMESTAMP, server_default=func.now())

class LeadRumah(Base):
    __tablename__ = "leads_rumah"
    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("rumah.id", ondelete="CASCADE")) # FK ikut ganti
    nama_buyer = Column(String(100))
    no_wa_buyer = Column(String(20))
    status = Column(Enum('Tanya', 'Survey', 'Booking', 'Akad', 'Gagal', name='lead_status_enum'), default='Tanya')
    fee_persen = Column(DECIMAL(4,2), default=2.00)
    nilai_fee = Column(BigInteger)
    tgl_akad = Column(Date)
    catatan = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    house = relationship("House")
