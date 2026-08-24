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
from routers import admin_mobil, admin_rumah, admin_showroom, admin_blog, admin_auth
from routers.admin_auth import require_admin

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

# HAPUS os.makedirs. Vercel gak bisa bikin folder pas runtime
# Kalau mau pake static, folder "static" harus udah ada di github dari awal
# Sementara kita komen dulu biar gak error
# app.mount("/static", StaticFiles(directory="static"), name="static")

# DAFTAR ROUTER SHOWROOM + UMUM
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(cars.router, prefix="/cars", tags=["Cars"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI"])
app.include_router(admin_auth.router, prefix="/admin-auth", tags=["Admin Auth"])

# DAFTAR ROUTER ADMIN
app.include_router(admin_showroom.router, prefix="/admin/showroom", tags=["Admin Showroom"])
app.include_router(admin_mobil.router, prefix="/admin/mobil", tags=["Admin Mobil"])
app.include_router(admin_rumah.router, prefix="/admin/rumah", tags=["Admin Rumah"])
app.include_router(admin_blog.router, prefix="/admin/blog", tags=["Admin Blog"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Otopadang API is running"}
