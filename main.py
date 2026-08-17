import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy.orm import Session

import models 
from database import engine, get_db

# IMPORT YG BARU UDAH DIPECAH
from routers import cars, houses, blog, ai_router, auth_router, showroom
from routers import admin_mobil, admin_rumah, admin_showroom, admin_blog # <-- GANTI INI

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

# DAFTAR ROUTER
app.include_router(auth_router.router)
app.include_router(showroom.router)
app.include_router(cars.router)
app.include_router(houses.router) 
app.include_router(blog.router)
app.include_router(ai_router.router)

# ADMIN ROUTER YG UDAH DIPECAH
app.include_router(admin_showroom.router)
app.include_router(admin_mobil.router)
app.include_router(admin_rumah.router)
app.include_router(admin_blog.router)

# HAPUS SEMUA ENDPOINT ADMIN MANUAL DI SINI
# @app.get("/admin/mobil") <-- HAPUS
# @app.put("/admin/mobil/{mobil_id}/approve") <-- HAPUS
# Karena udah ada di admin_mobil.py

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "cors": "enabled for vercel"}
