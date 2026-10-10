from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.auth_schema import LoginRequest

router = APIRouter()

@router.post("/login")
def admin_login(data: LoginRequest, db = Depends(get_db)):
    from app.models.admin import Admin
    admin = db.query(Admin).filter(Admin.email == data.email).first()
    if not admin or not verify_password(data.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    
    token = create_access_token({"sub": admin.email})
    return {"access_token": token, "token_type": "bearer"}
