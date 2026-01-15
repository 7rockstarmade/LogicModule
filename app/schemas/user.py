from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List

# Базовые поля пользователя
class UserBase(BaseModel):
    username: str
    full_name: str
    email: Optional[EmailStr] = None
    is_blocked: bool

    @field_validator("email", mode="before")
    def empty_email_to_none(cls, value):
        if value == "":
            return None
        return value

# Схема для создания пользователя
class UserCreate(BaseModel):
    username: str
    full_name: str
    email: Optional[EmailStr] = None
    is_blocked: bool

    @field_validator("email", mode="before")
    def empty_email_to_none(cls, value):
        if value == "":
            return None
        return value

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


class UserDataRead(BaseModel):
    id: int
    username: str
    roles: List[str] = []
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_blocked: bool

    courses_count: int
    attempts_count: int

    class Config:
        orm_mode = True


class UserMeRead(BaseModel):
    id: int
    full_name: Optional[str] = None

    class Config:
        orm_mode = True
