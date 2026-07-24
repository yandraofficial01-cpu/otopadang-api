import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
# from database import engine, Base  <-- HAPUS INI
import models 
from routers import cars, houses, blog, ai_router, auth_router, showroom

app = FastAPI(
    title="Otopadang API",
    description="API untuk Otopadang - Mobil, Rumah, Blog, AI",
    version="1.0.0",
    docs_url="/docs",          # <- Biar swagger muncul
    redoc_url="/redoc",        # <- Biar redoc muncul
    openapi_url="/openapi.json"
)

# 1. SETTING CORS - WAJIB BUAT NEXT.JS
origins = [
    "http://localhost:3000",  # Next.js dev
    "https://otpadang.com",   # Domain asli
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# 2. BIKIN FOLDER STATIC BISA DIAKSES
# Pastiin ada folder /static di root project
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. DAFTARIN SEMUA ROUTER
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(cars.router, prefix="/cars", tags=["Cars"])
app.include_router(houses.router, prefix="/houses", tags=["Houses"])
app.include_router(blog.router, prefix="/blog", tags=["Blog"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI"])
app.include_router(showroom.router, prefix="/showroom", tags=["Showroom"])

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

# 4. INI TAMBAHAN BUAT RAILWAY - WAJIB ADA
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
