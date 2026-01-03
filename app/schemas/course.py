from typing import Optional
from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class CourseRead(CourseBase):
    id: int
    teacher_id: int

    class Config:
        orm_mode = True

class CourseListRead(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True
