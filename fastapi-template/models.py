from datetime import datetime
from pydantic import BaseModel, HttpUrl


class URL(BaseModel):
    id: int
    original_url: HttpUrl
    short_url: str
    expiry_date: datetime
    clicks: int = 0
