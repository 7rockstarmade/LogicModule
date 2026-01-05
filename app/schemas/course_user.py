from pydantic import BaseModel
from datetime import datetime

class CourseUserCreate(BaseModel):
    course_id: int

class CourseUserRead(BaseModel):
    user_id: int
    enrolled_at: datetime

    class Config:
        orm_mode = True
