
from pydantic import BaseModel
from typing import Optional

class ShowroomCreate(BaseModel):
    name: str
    slug: str
    phone: Optional[str] = None
    address: Optional[str] = None

class ShowroomResponse(BaseModel):
    id: int
    name: str
    slug: str
    phone: Optional[str]
    address: Optional[str]
    class Config:
        from_attributes = True
