from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.question import (
    QuestionCreate,
    QuestionRead,
    QuestionVersionCreate,
    QuestionVersionRead,
)
from app.services.questions import (
    get_question_version,
    list_questions,
    _get_question_or_404,
    _get_question_version_or_404,
    create_question,
    create_question_version,
    delete_question,
    get_question
)

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("/", response_model=List[QuestionRead])
def api_list_questions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_questions(db, current_user)


@router.get("/{question_id}", response_model=QuestionVersionRead)
def api_get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return get_question(db, question_id, current_user)


@router.get("/{question_id}/versions/{version}")
def api_get_question_version(
    question_id: int,
    version: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return get_question_version(db, question_id, version, current_user)


@router.post("/", response_model=QuestionVersionRead, status_code=status.HTTP_201_CREATED)
def api_create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_question(db, payload, current_user)


@router.post("/{question_id}/versions", response_model=QuestionVersionRead, status_code=status.HTTP_201_CREATED)
def api_create_question_version(
    question_id: int,
    payload: QuestionVersionCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_question_version(db, question_id, payload, current_user)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    delete_question(db, question_id, current_user)
