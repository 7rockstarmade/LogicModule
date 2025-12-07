from pydantic import BaseModel

class CourseBase(BaseModel):
    title: str
    description: str

class CourseCreate(CourseBase):
    pass

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
