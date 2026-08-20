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
from routers import admin_mobil, admin_rumah, admin_showroom, admin_blog, admin_auth # 1. TAMBAH admin_auth
from routers.admin_auth import require_admin # 2. IMPORT DARI SINI

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
app.include_router(admin_auth.router) # 3. DAFTARIN INI

# DAFTAR ROUTER ADMIN
app.include_router(admin_showroom.router)
app.include_router(admin_mobil.router)
app.include_router(admin_rumah.router)
app.include_router(admin_blog.router)

# ... sisanya sama
