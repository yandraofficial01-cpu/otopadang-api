import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
import models 
from database import engine

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
    allow_credentials=True, # INI WAJIB TRUE KALAU PAKE TOKEN
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Biarin aja kalau masih ada foto lama
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.router)
app.include_router(admin_router)
app.include_router(showroom.router)
app.include_router(cars.router)
app.include_router(houses.router) 
app.include_router(blog.router)
app.include_router(ai_router.router)

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "cors": "enabled for vercel"}
