from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# Load semua model biar tabel ke-buat
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OtoPadang API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router - coba load satu2 biar gak crash kalau file belum ada
try:
    from app.routers import auth
    app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
except Exception as e:
    print(f"Auth router skip: {e}")

try:
    from app.routers import showrooms
    app.include_router(showrooms.router, prefix="/api/showrooms", tags=["Showrooms"])
except Exception as e:
    print(f"Showrooms router skip: {e}")

try:
    from app.routers import mobils
    app.include_router(mobils.router, prefix="/api/mobils", tags=["Mobils"])
except Exception as e:
    print(f"Mobils router skip: {e}")

try:
    from app.routers import blogs
    app.include_router(blogs.router, prefix="/api/blogs", tags=["Blogs"])
except Exception as e:
    print(f"Blogs router skip: {e}")

try:
    from app.routers import upload
    app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
except Exception as e:
    print(f"Upload router skip: {e}")

@app.get("/")
def root():
    return {"message": "OtoPadang API is running!", "status": "active", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
