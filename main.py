import os
from datetime import datetime
from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy.orm import Session

from models import Base 
from database import engine, get_db

# IMPORT SEMUA ROUTER PUBLIC
from routers import cars, rumah, ai_router, auth_router

# IMPORT SEMUA ROUTER ADMIN 
from routers import admin_mobil, admin_rumah, admin_showroom, admin_blog, admin_auth

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
        "https://otopadang-frontend-vtm8itdc9-yandraofficial01-9603s-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# ========== DAFTAR ROUTER PUBLIC ==========
app.include_router(auth_router.router, tags=["Auth"]) 
app.include_router(cars.router, prefix="/cars", tags=["Cars Public"])
app.include_router(rumah.router, tags=["Rumah Public"]) 
app.include_router(ai_router.router, prefix="/ai", tags=["AI"])

# ========== DAFTAR ROUTER ADMIN ==========
app.include_router(admin_auth.router, prefix="/admin/auth", tags=["Admin Auth"])
app.include_router(admin_showroom.router, tags=["Admin Showroom"])  # <--- HAPUS PREFIX
app.include_router(admin_mobil.router, tags=["Admin Mobil"])        # <--- HAPUS PREFIX  
app.include_router(admin_rumah.router, tags=["Admin Rumah"]) 
app.include_router(admin_blog.router, tags=["Admin Blog"])          # <--- HAPUS PREFIX

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Otopadang API is running"}
