from fastapi import Depends, HTTPException, status
from.auth_router import get_current_user
from models import User

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role!= "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak. Khusus Admin.")
    return current_user
