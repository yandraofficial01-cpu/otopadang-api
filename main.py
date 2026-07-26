import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 
import models 
from routers import cars, houses, blog, ai_router, auth_router, showroom

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
    "http://localhost:3000",            # Next.js dev
    "https://otpadang.com",             # Domain asli
    "https://www.otpadang.com",         # Domain pake www
    "https://otopadang-frontend.vercel.app"  # <- UDAH BENER INI
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(cars.router, prefix="/cars", tags=["Cars"])
app.include_router(houses.router, prefix="/houses", tags=["Houses"])
app.include_router(blog.router, prefix="/blog", tags=["Blog"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI"])
app.include_router(showroom.router, prefix="/showroom", tags=["Showroom"])

@app.get("/")
def read_root():
    return {"message": "Otopadang API Jalan Bro!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
