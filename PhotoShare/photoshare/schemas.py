from pydantic import BaseModel
from datetime import datetime

class ImageBase(BaseModel):
    url: str
    description: str
    rate: float
    url_view: str | None
    qr_code_view: str | None
    created_at: datetime
    user_id: int