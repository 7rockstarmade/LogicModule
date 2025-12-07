from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    full_name: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    is_blocked: bool
    roles: List[str] = [] 

    class Config:
        orm_mode = True
