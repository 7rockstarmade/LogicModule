from pydantic import BaseModel


class AnswerBase(BaseModel):
    value: int  # -1 если не отвечено, или номер варианта ответа


class AnswerUpdate(BaseModel):
    value: int


class AnswerRead(AnswerBase):
    id: int
    attempt_id: int
    question_id: int
    question_version_id: int

    class Config:
        orm_mode = True
