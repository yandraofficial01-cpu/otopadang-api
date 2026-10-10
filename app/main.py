from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OtoPadang API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTH
try:
    from app.routers.auth import admin_auth, showroom_auth
    app.include_router(admin_auth.router, prefix="/api/auth/admin", tags=["Auth Admin"])
    app.include_router(showroom_auth.router, prefix="/api/auth/showroom", tags=["Auth Showroom"])
except Exception as e:
    print(f"Auth skip: {e}")

# ADMIN
try:
    from app.routers.admin import showroom_router, mobil_router, blog_router
    app.include_router(showroom_router.router, prefix="/api/admin/showrooms", tags=["Admin Showroom"])
    app.include_router(mobil_router.router, prefix="/api/admin/mobils", tags=["Admin Mobil"])
    app.include_router(blog_router.router, prefix="/api/admin/blogs", tags=["Admin Blog"])
except Exception as e:
    print(f"Admin skip: {e}")

# PUBLIC - bikin file dummy biar main.py gak error
try:
    from app.routers import public
    app.include_router(public.router, prefix="/api", tags=["Public"])
except Exception as e:
    print(f"Public skip: {e}")

@app.get("/")
def root():
    return {"message": "OtoPadang API is running!", "status": "active", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
