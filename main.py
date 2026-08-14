import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy.orm import Session

import models 
from database import engine, get_db

from routers.admin_router import router as admin_router 
from routers import cars, houses, blog, ai_router, auth_router, showroom

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Otopadang API",
    description="API untuk Otopadang - Mobil, Rumah, Blog, AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.router.redirect_slashes = False 

# CORS FINAL BUAT VERCEL + TOKEN
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",            
        "https://otopadang.com",             
        "https://www.otopadang.com",         
        "https://otopadang-frontend.vercel.app", 
    ],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.router)
app.include_router(admin_router)
app.include_router(showroom.router)
app.include_router(cars.router)
app.include_router(houses.router) 
app.include_router(blog.router)
app.include_router(ai_router.router)

# ========== ENDPOINT ADMIN BARU ==========
# 0. AMBIL SEMUA MOBIL BUAT ADMIN <-- INI YG KURANG
@app.get("/admin/mobil")
def get_all_mobil(db: Session = Depends(get_db)):
    mobils = db.query(models.Car).order_by(models.Car.created_at.desc()).all()
    return mobils

# 1. APPROVE MOBIL
@app.put("/admin/mobil/{mobil_id}/approve")
def approve_mobil(mobil_id: int, db: Session = Depends(get_db)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    mobil.status = "approved"
    db.commit()
    db.refresh(mobil)
    return {"message": "Mobil berhasil diapprove", "data": mobil}

# 2. TANDAI SOLD
@app.put("/admin/mobil/{mobil_id}/sold")
def sold_mobil(mobil_id: int, db: Session = Depends(get_db)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    mobil.status = "sold"
    mobil.sold_at = datetime.utcnow()
    db.commit()
    db.refresh(mobil)
    return {"message": "Mobil ditandai SOLD", "data": mobil}

# 3. HAPUS PERMANEN
@app.delete("/admin/mobil/{mobil_id}")
def delete_mobil(mobil_id: int, db: Session = Depends(get_db)):
    mobil = db.query(models.Car).filter(models.Car.id == mobil_id).first()
    if not mobil:
        raise HTTPException(status_code=404, detail="Mobil tidak ditemukan")
    
    nama = mobil.nama_mobil
    db.delete(mobil)
    db.commit()
    return {"message": f"Mobil {nama} berhasil dihapus permanen"}

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "cors": "enabled for vercel"}
