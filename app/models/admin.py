from app import db
from datetime import datetime

class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('superadmin', 'showroom'), nullable=False, default='showroom')
    showroom_id = db.Column(db.Integer, db.ForeignKey('showrooms.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Admin {self.email} - {self.role}>"
