from sqlalchemy import Column, Integer, String, BigInteger, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Mobil(Base):
    __tablename__ = "mobils"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id", ondelete="CASCADE"), nullable=False)

    merk = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    tahun = Column(Integer, nullable=False)
    harga = Column(BigInteger, nullable=False)
    transmisi = Column(String(20), nullable=False) # Manual / Matic
    kilometer = Column(Integer, nullable=False)
    bahan_bakar = Column(String(20), nullable=False) # Bensin / Solar / Listrik
    warna = Column(String(50), nullable=False)

    # FINAL 12 KOLOM
    foto_urls = Column(JSON, nullable=True, comment="Array 8 URL Cloudinary")
    wa_admin = Column(String(20), nullable=True, comment="WA admin per mobil")

    deskripsi = Column(Text, nullable=True)
    is_sold = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relasi - HAPUS back_populates biar gak error kalau di Showroom gak ada
    showroom = relationship("Showroom")
