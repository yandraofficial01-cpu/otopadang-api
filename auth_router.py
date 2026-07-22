from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import get_db
from models import UserShowroom
from auth import hash_password, verify_password # <- import dari Backend/auth.py

router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    showroom_id: int 

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    cek = db.query(UserShowroom).filter(UserShowroom.email == user.email).first()
    if cek: 
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    
    hashed = hash_password(user.password) # pake dari auth.py
    new_user = UserShowroom(email=user.email, password=hashed, showroom_id=user.showroom_id)
    db.add(new_user); db.commit(); db.refresh(new_user)
    return {"msg": "Register berhasil", "id": new_user.id, "showroom_id": new_user.showroom_id}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserShowroom).filter(UserShowroom.email == user.email).first()
    if not db_user: 
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    if not verify_password(user.password, db_user.password): # pake dari auth.py
        raise HTTPException(status_code=400, detail="Email atau password salah")
    
    return {"msg": "Login berhasil", "showroom_id": db_user.showroom_id, "email": db_user.email}