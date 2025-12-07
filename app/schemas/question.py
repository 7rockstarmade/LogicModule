from pydantic import BaseModel
from typing import List

class QuestionBase(BaseModel):
    title: str
    text: str
    options: List[str]
    correct_index: int

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    id: int

    class Config:
        orm_mode = True

class QuestionVersionCreate(BaseModel):
    title: str
    text: str
    options: List[str]
    correct_index: int

    class Config:
        orm_mode = True
