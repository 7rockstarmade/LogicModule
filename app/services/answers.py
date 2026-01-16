from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import Permissions, ensure_default_or_permission
from app.core.security import CurrentUser
from app.models.answers import Answer
from app.models.attempts import Attempt
from app.models.courses import Course
from app.models.question_versions import QuestionVersion
from app.models.tests import Test


ATTEMPT_STATUS_FINISHED = "finished"


def _get_answer_or_404(db: Session, answer_id: int) -> Answer:
    ans = db.query(Answer).filter(Answer.id == answer_id).first()
    if not ans:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    return ans


def _get_attempt_or_404(db: Session, attempt_id: int) -> Attempt:
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    return attempt


def _get_test_or_404(db: Session, test_id: int) -> Test:
    test = db.query(Test).filter(Test.id == test_id, Test.is_deleted == False).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    return test


def _get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted == False).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


def _is_course_teacher(course: Course, current_user: CurrentUser) -> bool:
    return course.teacher_id == current_user.id


def _validate_answer_value(db: Session, ans: Answer, value: int) -> None:
    if value == -1:
        return
    qv = db.query(QuestionVersion).filter(QuestionVersion.id == ans.question_version_id).first()
    if not qv:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question version not found")

    if not isinstance(qv.options, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question options")

    if value < 0 or value >= len(qv.options):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Answer value out of range")

# ---------------- Бизнес-логика ----------------

def list_attempt_answers(db: Session, attempt_id: int, current_user: CurrentUser) -> list[Answer]:
    """
    GET answers of attempt.

    default:
      - владелец попытки
      - преподаватель курса теста
    иначе:
      - permission answer:read
    """
    attempt = _get_attempt_or_404(db, attempt_id)
    test = _get_test_or_404(db, attempt.test_id)
    course = _get_course_or_404(db, test.course_id)

    default_allowed = (attempt.user_id == current_user.id) or _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.ANSWER_READ,
        msg="You do not have access to these answers",
        user_roles=current_user.roles,
    )

    return db.query(Answer).filter(Answer.attempt_id == attempt_id).all()


def update_answer(db: Session, answer_id: int, value: int, current_user: CurrentUser) -> Answer:
    """
    PATCH answer.

    default:
      - владелец попытки
    иначе:
      - permission answer:update

    ограничения:
      - нельзя менять, если attempt finished
      - value = -1 или индекс в диапазоне вариантов
    """
    ans = _get_answer_or_404(db, answer_id)
    attempt = _get_attempt_or_404(db, ans.attempt_id)

    default_allowed = attempt.user_id == current_user.id
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.ANSWER_UPDATE,
        msg="You do not have permission to update this answer",
        user_roles=current_user.roles,
    )

    if attempt.status == ATTEMPT_STATUS_FINISHED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attempt is finished")

    _validate_answer_value(db, ans, value)

    ans.value = value
    db.add(ans)
    db.commit()
    db.refresh(ans)
    return ans


def reset_answer(db: Session, answer_id: int, current_user: CurrentUser) -> Answer:
    """
    DELETE /answers/{answer_id}
    По ТЗ: это "сброс", т.е. value = -1

    default:
      - владелец попытки
    иначе:
      - permission answer:del
    """
    ans = _get_answer_or_404(db, answer_id)
    attempt = _get_attempt_or_404(db, ans.attempt_id)

    default_allowed = attempt.user_id == current_user.id
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.ANSWER_DEL,
        msg="You do not have permission to delete this answer",
        user_roles=current_user.roles,
    )

    if attempt.status == ATTEMPT_STATUS_FINISHED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attempt is finished")

    ans.value = -1
    db.add(ans)
    db.commit()
    db.refresh(ans)
    return ans
