import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
from database import engine, Base
import models # penting biar tabel kebaca
from routers import cars, houses, blog, ai_router, auth_router, showroom

app = FastAPI(title="Otopadang API")

# 1. BIKIN TABEL OTOMATIS PAS STARTUP - JANGAN DI GLOBAL
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# 2. SETTING CORS - WAJIB BUAT NEXT.JS
origins = [
    "http://localhost:3000",  # Next.js dev
    "https://otpadang.com",   # Nanti domain asli
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# 3. BIKIN FOLDER STATIC BISA DIAKSES
app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. DAFTARIN SEMUA ROUTER
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(cars.router, prefix="/cars", tags=["Cars"])
app.include_router(houses.router, prefix="/houses", tags=["Houses"])
app.include_router(blog.router, prefix="/blog", tags=["Blog"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI"])
app.include_router(showroom.router, prefix="/showroom", tags=["Showroom"])

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

# 5. INI TAMBAHAN BUAT RAILWAY - WAJIB ADA
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
