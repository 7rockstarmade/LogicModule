from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class TestActiveUpdate(BaseModel):
    is_active: bool


class TestQuestionAdd(BaseModel):
    question_id: int


class TestQuestionsOrderUpdate(BaseModel):
    question_ids: List[int] = Field(..., min_length=1)


class TestResultUser(BaseModel):
    id: int
    full_name: str

    class Config:
        orm_mode = True


class TestGradeItem(BaseModel):
    attempt_id: int
    user_id: int
    finished_at: datetime
    score: Optional[Decimal] = None

    class Config:
        orm_mode = True


class TestAnswerItem(BaseModel):
    answer_id: int
    question_id: int
    question_version_id: int
    value: int
    correct_index: int
    is_correct: bool


class TestAttemptAnswers(BaseModel):
    attempt_id: int
    user_id: int
    finished_at: datetime
    score: Optional[Decimal] = None
    answers: List[TestAnswerItem]
