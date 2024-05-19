from pydantic import BaseModel
from datetime import datetime


class ImageCreate(BaseModel):
    url: str
    description: str
    created_at: datetime


class ImageDB(ImageCreate):
    id: int
    likes: int
    dislikes: int
    rate: float
    url_view: str | None
    qr_code_view: str | None
    user_id: int


class ImageUpdate(BaseModel):
    description: str
