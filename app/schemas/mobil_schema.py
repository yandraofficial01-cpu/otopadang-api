from pydantic import BaseModel
from typing import Optional

class MobilCreate(BaseModel):
    title: str
    price: int
    year: Optional[int] = None
    description: Optional[str] = None

class MobilResponse(BaseModel):
    id: int
    title: str
    price: int
    year: Optional[int]
    showroom_id: int
    class Config:
        from_attributes = True
