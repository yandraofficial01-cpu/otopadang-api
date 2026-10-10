from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.database import SessionLocal
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "otopadang-secret-key-123")
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_admin(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    from app.models.admin import Admin
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalid")
        admin = db.query(Admin).filter(Admin.email == email).first()
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        return admin
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid")
