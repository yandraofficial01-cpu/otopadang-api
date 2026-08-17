import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 

import models 
from database import engine

# IMPORT ROUTER SHOWROOM + UMUM
from routers import cars, ai_router, auth_router

# IMPORT ROUTER ADMIN 
from routers import admin_mobil, admin_rumah, admin_showroom, admin_blog

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

# DAFTAR ROUTER SHOWROOM + UMUM
app.include_router(auth_router.router)  # /login /register
app.include_router(cars.router)         # /cars buat showroom upload/edit
app.include_router(ai_router.router)    # /ai

# DAFTAR ROUTER ADMIN
app.include_router(admin_showroom.router) # /admin/showroom
app.include_router(admin_mobil.router)    # /admin/mobil approve/soldout/delete
app.include_router(admin_rumah.router)    # /admin/rumah
app.include_router(admin_blog.router)     # /admin/blog

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "cors": "enabled for vercel"}
