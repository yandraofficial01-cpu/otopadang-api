from sqlalchemy import Column, Integer, String, BigInteger, Text, Enum, DECIMAL, Date, TIMESTAMP, ForeignKey
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
    paket = Column(Enum('Basic', 'Premium'), default='Basic')
    status_bayar = Column(Enum('aktif', 'expired'), default='aktif')
    
    # BUAT APPROVE ADMIN
    status = Column(Enum('pending', 'approved', 'rejected'), default='pending', nullable=False) 
    
    tgl_expired = Column(Date)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    cars = relationship("Car", back_populates="showroom", cascade="all, delete-orphan")
    users = relationship("User", back_populates="showroom", cascade="all, delete-orphan") # GANTI JADI User
    # RELASI HOUSE DIHAPUS


class User(Base): # GANTI NAMA CLASS
    __tablename__ = "users" # GANTI INI
    id = Column(Integer, primary_key=True, index=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id", ondelete="CASCADE"), nullable=True)
    
    # TAMBAHIN KOLOM YG ADA DI DB LU
    name = Column(String(255), nullable=True)  # lu ada di DB
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True) # lu ada di DB
    role = Column(String(50), default='showroom') # PENTING
    status = Column(String(50), default='active') # PENTING
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
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
    
    status = Column(Enum('pending', 'approved', 'ready', 'sold'), default='pending')
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    showroom = relationship("Showroom", back_populates="cars")


class House(Base):
    __tablename__ = "houses"
    id = Column(Integer, primary_key=True, index=True)
    nama_rumah = Column(String(100))
    tipe = Column(String(50))
    alamat = Column(Text)
    harga = Column(BigInteger)
    harga_kredit = Column(BigInteger)
    angsuran = Column(BigInteger)
    lama_angsuran = Column(Integer)
    luas_tanah = Column(Integer)
    luas_bangunan = Column(Integer)
    spesifikasi = Column(Text)
    badge_bonus = Column(String(50))
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
    status = Column(Enum('available', 'sold'), default='available')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class LeadRumah(Base):
    __tablename__ = "leads_rumah"
    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("houses.id", ondelete="CASCADE"))
    nama_buyer = Column(String(100))
    no_wa_buyer = Column(String(20))
    status = Column(Enum('Tanya', 'Survey', 'Booking', 'Akad', 'Gagal'), default='Tanya')
    fee_persen = Column(DECIMAL(4,2), default=2.00)
    nilai_fee = Column(BigInteger)
    tgl_akad = Column(Date)
    catatan = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    house = relationship("House")
