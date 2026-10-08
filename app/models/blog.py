from sqlalchemy import Column, BigInteger, String, Text, Integer, TIMESTAMP
from sqlalchemy import Boolean as TinyInt
from sqlalchemy.sql import func
from database import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    judul = Column(String(200), nullable=False)
    slug = Column(String(250), nullable=False, unique=True)
    kategori = Column(String(50), nullable=False, index=True)
    thumbnail = Column(Text, nullable=True) # URL Cloudinary
    excerpt = Column(String(300), nullable=True)
    konten = Column(Text().with_variant(Text(4294967295), 'mysql'), nullable=False) # LONGTEXT
    tags = Column(String(200), nullable=True)
    author_name = Column(String(100), nullable=True, default="Admin OtoPadang")
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(300), nullable=True)
    views = Column(Integer, nullable=True, default=0)
    is_published = Column(TinyInt, nullable=True, default=0, index=True)
    published_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=True, server_default=func.now(), onupdate=func.now())
