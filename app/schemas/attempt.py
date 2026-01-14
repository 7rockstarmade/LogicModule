from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class AttemptRead(BaseModel):
    id: int
    user_id: int
    test_id: int
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    score: Optional[Decimal] = None

    class Config:
        orm_mode = True
