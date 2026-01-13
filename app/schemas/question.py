from typing import List, Optional

from pydantic import BaseModel, Field


class QuestionBase(BaseModel):
    title: str
    text: str
    options: List[str]
    correct_index: int


class QuestionCreate(QuestionBase):
    test_id: Optional[int] = None


class QuestionVersionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    id: int = Field(..., description="ID версии (question_versions.id)")
    question_id: int
    version: int
    author_id: int

    class Config:
        from_attributes = True


class QuestionVersionRead(QuestionBase):
    id: int
    question_id: int
    version: int

    class Config:
        from_attributes = True
