from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.answer import AnswerRead, AnswerUpdate
from app.services.answers import list_attempt_answers, reset_answer, update_answer

router = APIRouter(prefix="/api/answers", tags=["Answers"])


@router.get("/attempts/{attempt_id}", response_model=list[AnswerRead])
def api_list_attempt_answers(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_attempt_answers(db, attempt_id, current_user)


@router.patch("/{answer_id}", response_model=AnswerRead)
def api_update_answer(
    answer_id: int,
    payload: AnswerUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return update_answer(db, answer_id, payload.value, current_user)


@router.delete("/{answer_id}", response_model=AnswerRead)
def api_reset_answer(
    answer_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return reset_answer(db, answer_id, current_user)
