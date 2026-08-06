import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
import models 
from database import engine # BUAT BIKIN TABEL

# IMPORT SEMUA ROUTER
from routers.admin_router import router as admin_router 
from routers import cars, houses, blog, ai_router, auth_router, showroom

# BIKIN TABEL OTOMATIS PAS START
# Catatan: di production sebaiknya pake Alembic
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Otopadang API",
    description="API untuk Otopadang - Mobil, Rumah, Blog, AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 1. SETTING CORS - PENTING BUAT FE VERCEL
origins = [
    "http://localhost:3000",            
    "http://localhost:5173",            
    "https://otopadang.com",             
    "https://www.otopadang.com",         
    "https://otopadang-frontend.vercel.app", # domain vercel yg lu set manual
    "https://frontend.vercel.app",           # <-- TAMBAHIN INI. Ini yg di SS lu
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# 2. MOUNT STATIC BUAT FOTO
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. DAFTARIN SEMUA ROUTER URUT
app.include_router(auth_router.router) # Auth dulu, biar bisa login
app.include_router(admin_router)       # Menu Admin
app.include_router(showroom.router)    # Dashboard Showroom
app.include_router(cars.router)        # Mobil - prefix udah di dalem cars.py
app.include_router(houses.router)      # Rumah - prefix udah di dalem houses.py
app.include_router(blog.router)        # Blog
app.include_router(ai_router.router)   # AI

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
