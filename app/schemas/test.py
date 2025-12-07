from pydantic import BaseModel

class TestBase(BaseModel):
    title: str
    is_active: bool = False

class TestCreate(TestBase):
    pass

class TestRead(TestBase):
    id: int
    course_id: int

    class Config:
        orm_mode = True

class TestListRead(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True
