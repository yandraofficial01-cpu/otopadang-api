import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
import models 
from database import engine

# IMPORT SEMUA ROUTER
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

# 1. SETTING CORS - FIX BIAR GAK FAILED TO FETCH
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",  # ALLOW SEMUA DEPLOY VERCEL (preview & production)
    allow_origins=[
        "http://localhost:3000",            
        "http://localhost:5173",            
        "https://otopadang.com",             
        "https://www.otopadang.com",         
        "https://otopadang-frontend.vercel.app",
        "https://frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# 2. MOUNT STATIC BUAT FOTO
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. DAFTARIN SEMUA ROUTER URUT
app.include_router(auth_router.router)
app.include_router(admin_router)
app.include_router(showroom.router)
app.include_router(cars.router)
app.include_router(houses.router, prefix="/rumah", tags=["Rumah Publik"]) # <-- FIX DI SINI
app.include_router(blog.router)
app.include_router(ai_router.router)

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "cors": "enabled for vercel"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
