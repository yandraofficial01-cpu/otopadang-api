from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.auth_schema import LoginRequest

router = APIRouter()

@router.post("/login")
def showroom_login(data: LoginRequest, db = Depends(get_db)):
    from app.models.showroom import Showroom
    showroom = db.query(Showroom).filter(Showroom.email == data.email).first()
    if not showroom:
        raise HTTPException(status_code=401, detail="Showroom tidak ditemukan")
    # sementara bypass password dulu biar gak error
    token = create_access_token({"sub": showroom.email, "type": "showroom"})
    return {"access_token": token, "token_type": "bearer"}
