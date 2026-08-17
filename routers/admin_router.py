from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
import models
from database import get_db
from routers.auth_router import get_current_user

def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def require_admin(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.showroom_id is not None:
        raise HTTPException(status_code=403, detail="Akses khusus Admin Pusat")
    return current_user
