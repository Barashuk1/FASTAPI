from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True

class ImageBase(BaseModel):
    url: str
    description: str
    created_at: datetime

class ImageModel(ImageBase):
    tags: List[int]

class ImageDB(ImageBase):
    id: int
    likes: int
    dislikes: int
    rate: float
    url_view: str | None
    qr_code_view: str | None
    tags: List[TagResponse]
    user_id: int


class ImageUpdate(ImageModel):
    description: str
