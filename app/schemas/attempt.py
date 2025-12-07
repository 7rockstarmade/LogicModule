from pydantic import BaseModel
from typing import Optional

class AttemptBase(BaseModel):
    status: str
    score: Optional[float] = None

class AttemptCreate(AttemptBase):
    pass

class AttemptRead(AttemptBase):
    id: int
    user_id: int
    test_id: int
    started_at: str
    finished_at: Optional[str] = None

    class Config:
        orm_mode = True
