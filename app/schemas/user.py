from pydantic import BaseModel, EmailStr
from typing import Optional

# Базовые поля пользователя
class UserBase(BaseModel):
    username: str
    full_name: str
    email: Optional[EmailStr] = None
    is_blocked: bool

# Схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    full_name: str
    email: Optional[EmailStr] = None
    is_blocked: bool

# Схема для чтения пользователя (отправляется клиенту)
class UserRead(UserBase):
    id: int
    class Config:
        orm_mode = True

# Схема для обновления пользователя
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_blocked: Optional[bool] = None # Если вдруг надо будет забанить пользователя

    class Config:
        orm_mode = True
