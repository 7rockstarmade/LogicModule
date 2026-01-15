from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: int
    message: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        orm_mode = True
