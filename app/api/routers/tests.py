from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.test import TestRead, TestCreate
from app.schemas.tests_extra import (
    TestActiveUpdate,
    TestQuestionAdd,
    TestQuestionsOrderUpdate,
    TestResultUser,
    TestGradeItem,
    TestAttemptAnswers,
)

from app.services.tests import (
    create_test,
    delete_test,
    get_test_active_status,
    set_test_active_status,
    add_question_to_test,
    remove_question_from_test,
    reorder_test_questions,
    list_test_result_users,
    list_test_grades,
    list_test_answers,
)

router = APIRouter(prefix='/api', tags=["Tests"])


# 3.1
@router.post("/courses/{course_id}/tests", response_model=TestRead, status_code=status.HTTP_201_CREATED)
def api_create_test(
    course_id: int,
    payload: TestCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_test(db, course_id, payload.title, payload.is_active, current_user)


# 3.2
@router.delete("/courses/{course_id}/tests/{test_id}", response_model=TestRead)
def api_delete_test(
    course_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return delete_test(db, course_id, test_id, current_user)


# 3.3
@router.get("/courses/{course_id}/tests/{test_id}/active")
def api_get_test_active_status(
    course_id: int,
    test_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return get_test_active_status(db, course_id, test_id, current_user)


# 3.4 (BODY)
@router.patch("/courses/{course_id}/tests/{test_id}/active", response_model=TestRead)
def api_set_test_active_status(
    course_id: int,
    test_id: int,
    payload: TestActiveUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return set_test_active_status(db, course_id, test_id, current_user, payload.is_active)


# 3.5
@router.post("/tests/{test_id}/questions", status_code=status.HTTP_201_CREATED)
def api_add_question_to_test(
    test_id: int,
    payload: TestQuestionAdd,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    link = add_question_to_test(db, test_id, payload.question_id, current_user)
    return {"test_id": link.test_id, "question_id": link.question_id, "position": link.position}


# 3.6
@router.delete("/tests/{test_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_remove_question_from_test(
    test_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    remove_question_from_test(db, test_id, question_id, current_user)
    return None


# 3.7
@router.put("/tests/{test_id}/questions/order")
def api_reorder_test_questions(
    test_id: int,
    payload: TestQuestionsOrderUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    links = reorder_test_questions(db, test_id, payload.question_ids, current_user)
    return [{"test_id": x.test_id, "question_id": x.question_id, "position": x.position} for x in links]


# 3.8
@router.get("/tests/{test_id}/results/users", response_model=List[TestResultUser])
def api_list_test_result_users(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_test_result_users(db, test_id, current_user)


# 3.9
@router.get("/tests/{test_id}/results/grades", response_model=List[TestGradeItem])
def api_list_test_grades(
    test_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    attempts = list_test_grades(db, test_id, current_user, user_id)
    return [
        {
            "attempt_id": a.id,
            "user_id": a.user_id,
            "finished_at": a.finished_at,
            "score": a.score,
        }
        for a in attempts
    ]


# 3.10
@router.get("/tests/{test_id}/results/answers", response_model=List[TestAttemptAnswers])
def api_list_test_answers(
    test_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    data = list_test_answers(db, test_id, current_user, user_id)
    return data
