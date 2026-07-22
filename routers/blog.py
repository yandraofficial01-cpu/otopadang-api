from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_blog():
    return {"message": "API Blog Jalan - Nanti isi artikel otomotif & properti"}
