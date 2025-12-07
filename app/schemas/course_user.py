from pydantic import BaseModel
from datetime import datetime

class CourseUserBase(BaseModel):
    course_id: int
    user_id: int
    enrolled_at: datetime

class CourseUserCreate(CourseUserBase):
    pass

class CourseUserRead(CourseUserBase):
    class Config:
        orm_mode = True
