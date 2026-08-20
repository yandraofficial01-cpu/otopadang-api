import os
from datetime import datetime
from fastapi import FastAPI, Depends, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy.orm import Session

import models 
from database import engine, get_db

# IMPORT ROUTER SHOWROOM + UMUM
from routers import cars, ai_router, auth_router

# IMPORT ROUTER ADMIN 
from routers import admin_mobil, admin_rumah, admin_showroom, admin_blog
from routers.auth_router import get_current_admin

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

# DAFTAR ROUTER SHOWROOM + UMUM
app.include_router(auth_router.router)
app.include_router(cars.router)
app.include_router(ai_router.router)

# DAFTAR ROUTER ADMIN - HAPUS PREFIX DISINI
app.include_router(admin_showroom.router)
app.include_router(admin_mobil.router)
app.include_router(admin_rumah.router)
app.include_router(admin_blog.router)

# ================== ROUTER BARU UNTUK DASHBOARD ==================
admin_dashboard_router = APIRouter()

@admin_dashboard_router.get("/admin/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    total_mobil = db.query(models.Car).count()
    total_pending = db.query(models.Car).filter(models.Car.status == 'pending').count()
    total_showroom = db.query(models.Showroom).count()
    total_rumah = db.query(models.Rumah).count()
    total_blog = db.query(models.Blog).count()
    
    mobil_baru_query = db.query(models.Car).filter(models.Car.status == 'pending').order_by(models.Car.created_at.desc()).limit(5).all()

    return {
        "total_mobil": total_mobil,
        "total_pending": total_pending,
        "total_showroom": total_showroom,
        "total_rumah": total_rumah,
        "total_blog": total_blog,
        "mobil_baru": [{"id": m.id, "merk": m.merk, "tipe": m.tipe} for m in mobil_baru_query]
    }

app.include_router(admin_dashboard_router)
# =================================================================

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "cors": "enabled for vercel"}
