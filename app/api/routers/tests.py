from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import CurrentUser, get_current_user
from app.schemas.test import TestRead
from app.models.tests import Test
from app.services.tests import (
    create_test,
    delete_test,
    get_test_active_status,
    set_test_active_status,
)

router = APIRouter(tags=["Tests"])


@router.post(
    "/courses/{course_id}/tests",
    response_model=TestRead,
    status_code=status.HTTP_201_CREATED,
)
def api_create_test(
    course_id: int,
    title: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_test(db, course_id, current_user, title)


@router.delete(
    "/courses/{course_id}/tests/{test_id}",
    response_model=TestRead,
)
def api_delete_test(
    course_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return delete_test(db, course_id, test_id, current_user)


@router.get(
    "/courses/{course_id}/tests/{test_id}/active",
)
def api_get_test_active_status(
    course_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return {
        "is_active": get_test_active_status(
            db,
            course_id,
            test_id,
            current_user,
        )
    }


@router.patch(
    "/courses/{course_id}/tests/{test_id}/active",
    response_model=TestRead,
)
def api_set_test_active_status(
    course_id: int,
    test_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return set_test_active_status(
        db,
        course_id,
        test_id,
        current_user,
        is_active,
    )
