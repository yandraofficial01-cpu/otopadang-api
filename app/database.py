from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Ambil URL dari Railway Variables
DATABASE_URL = os.getenv("DATABASE_URL")

# TiDB butuh ini biar gak error SSL
if DATABASE_URL and "ssl_verify" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&ssl_verify_cert=true&ssl_verify_identity=true"
    else:
        DATABASE_URL += "?ssl_verify_cert=true&ssl_verify_identity=true"

# Fix postgres:// jadi postgresql:// kalau kebalik
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
