from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.attempt import AttemptRead
from app.services.attempts import create_attempt, finish_attempt, get_attempt

router = APIRouter(prefix="/api/attempts", tags=["Attempts"])


@router.post("/tests/{test_id}", response_model=AttemptRead, status_code=status.HTTP_201_CREATED)
def api_create_attempt(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_attempt(db, test_id, current_user)


@router.get("/{attempt_id}", response_model=AttemptRead)
def api_get_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return get_attempt(db, attempt_id, current_user)


@router.post("/{attempt_id}/finish", response_model=AttemptRead)
def api_finish_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return finish_attempt(db, attempt_id, current_user)
