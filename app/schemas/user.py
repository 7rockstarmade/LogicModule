from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    full_name: str
    email: Optional[EmailStr] = None
    is_blocked: bool

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None

    class Config:
        orm_mode = True