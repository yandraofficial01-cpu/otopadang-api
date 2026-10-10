from pydantic import BaseModel
from typing import Optional

class BlogCreate(BaseModel):
    title: str
    content: str
    slug: Optional[str] = None

class BlogResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    class Config:
        from_attributes = True
