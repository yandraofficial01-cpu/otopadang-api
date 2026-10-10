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
from app.routers.auth import admin_auth, showroom_auth
app.include_router(admin_auth.router, prefix="/api/auth/admin", tags=["Auth Admin"])
app.include_router(showroom_auth.router, prefix="/api/auth/showroom", tags=["Auth Showroom"])

# ADMIN
from app.routers.admin import showroom_router as admin_showroom
from app.routers.admin import mobil_router as admin_mobil
from app.routers.admin import blog_router as admin_blog
app.include_router(admin_showroom.router, prefix="/api/admin/showrooms", tags=["Admin Showroom"])
app.include_router(admin_mobil.router, prefix="/api/admin/mobils", tags=["Admin Mobil"])
app.include_router(admin_blog.router, prefix="/api/admin/blogs", tags=["Admin Blog"])

# PUBLIC
from app.routers.public import mobil_router as public_mobil
from app.routers.public import showroom_router as public_showroom
app.include_router(public_mobil.router, prefix="/api/mobils", tags=["Public Mobil"])
app.include_router(public_showroom.router, prefix="/api/showrooms", tags=["Public Showroom"])

@app.get("/")
def root():
    return {"message": "OtoPadang API is running!", "status": "active", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
