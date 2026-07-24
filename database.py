from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# HARDCODE BUAT RAILWAY - JANGAN PAKE ENV DULU
DATABASE_URL = "mysql+pymysql://2LjCFgMS6ZcPP1b.root:kBblzkLDr7tSH6oh@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"ssl": {"ssl_verify_cert": False}}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
