from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class Showroom(Base):
    __tablename__ = "showrooms"

    # 9 KOLOM INTI SESUAI DB OTOPADANG
    id = Column(Integer, primary_key=True, autoincrement=True) # 1
    nama = Column(String(255), nullable=False) # 2
    slug = Column(String(255), unique=True, nullable=False, index=True) # 3
    alamat = Column(Text, nullable=False) # 4
    kota = Column(String(100), nullable=True, default="Padang") # 5
    whatsapp = Column(String(20), nullable=False) # 6
    logo_url = Column(String(500), nullable=True) # 7 - di sheet lu ke-detect logo_uri, tapi kita pake logo_url
    deskripsi = Column(Text, nullable=True) # 8
    is_active = Column(Boolean, default=True) # 9

    # BONUS TIMESTAMP (otomatis)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
