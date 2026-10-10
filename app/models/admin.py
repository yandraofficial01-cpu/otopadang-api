from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from datetime import datetime
from app.database import Base

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    nama = Column(String(255), nullable=False)
    role = Column(Enum('superadmin', 'showroom'), nullable=False, default='showroom')
    showroom_id = Column(Integer, ForeignKey('showrooms.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Admin {self.email} - {self.role}>"
