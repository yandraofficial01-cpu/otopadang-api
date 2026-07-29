import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
import models 
from database import engine # BUAT BIKIN TABEL

# FIX: IMPORT DARI routers.admin_router BUKAN auth
from routers.admin_router import router as admin_router 
from routers import cars, houses, blog, ai_router, auth_router, showroom

# BIKIN TABEL OTOMATIS PAS START
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Otopadang API",
    description="API untuk Otopadang - Mobil, Rumah, Blog, AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 1. SETTING CORS - UDAH FIX
origins = [
    "http://localhost:3000",            
    "https://otpadang.com",             
    "https://www.otpadang.com",         
    "https://otopadang-frontend.vercel.app"  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ROUTER BARU
app.include_router(admin_router) # <-- UDAH GA PERLU prefix LAGI. UDAH ADA DI admin_router.py
app.include_router(auth_router.router)

# ROUTER LAMA KAMU
app.include_router(cars.router, prefix="/cars", tags=["Cars"])
app.include_router(houses.router, prefix="/houses", tags=["Houses"])
app.include_router(blog.router, prefix="/blog", tags=["Blog"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI"])
app.include_router(showroom.router, prefix="/showroom", tags=["Showroom"])

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

if __name__ == "__main__": # <-- FIX TYPO DISINI
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
