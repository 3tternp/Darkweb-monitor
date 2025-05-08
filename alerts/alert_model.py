from pydantic import BaseModel
from datetime import datetime

class Alert(BaseModel):
    id: int
    keyword: str
    source: str
    date: datetime
    message: str

    class Config:
        orm_mode = True

