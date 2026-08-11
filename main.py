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
    version="1.0.0",
    docs_url="/docs",
)

# FIX CORS FINAL BOSS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ # SEBUTIN SEMUA DOMAIN VERCEL LU 1-1
        "http://localhost:3000",            
        "https://otopadang-frontend.vercel.app",
        "https://frontend.vercel.app", # INI YG DI SS LU
    ],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

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
