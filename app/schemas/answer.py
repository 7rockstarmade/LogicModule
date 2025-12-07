from pydantic import BaseModel
from typing import Optional

class AnswerBase(BaseModel):
    value: int  # -1 если не отвечено, или номер варианта ответа

class AnswerCreate(AnswerBase):
    pass

class AnswerRead(AnswerBase):
    id: int
    attempt_id: int
    question_id: int
    question_version_id: int

    class Config:
        orm_mode = True
