from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import Permissions, ensure_default_or_permission
from app.core.security import CurrentUser
from app.models.attempts import Attempt
from app.models.attempts_questions import AttemptQuestion
from app.models.answers import Answer
from app.models.courses import Course
from app.models.course_users import CourseUser
from app.models.question_versions import QuestionVersion
from app.models.tests import Test
from app.models.test_questions import TestQuestion


ATTEMPT_STATUS_IN_PROGRESS = "in_progress"
ATTEMPT_STATUS_FINISHED = "finished"


# ---------------- helpers ----------------

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


def _is_student_enrolled(db: Session, course_id: int, user_id: int) -> bool:
    return (
        db.query(CourseUser)
        .filter(CourseUser.course_id == course_id, CourseUser.user_id == user_id)
        .first()
        is not None
    )


def _get_attempt_or_404(db: Session, attempt_id: int) -> Attempt:
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    return attempt


def _get_latest_question_version_or_404(db: Session, question_id: int) -> QuestionVersion:
    qv = (
        db.query(QuestionVersion)
        .filter(QuestionVersion.question_id == question_id)
        .order_by(QuestionVersion.version.desc())
        .first()
    )
    if not qv:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question has no versions: question_id={question_id}",
        )
    return qv


def _has_any_attempts_for_test(db: Session, test_id: int) -> bool:
    return db.query(Attempt).filter(Attempt.test_id == test_id).first() is not None


# ---------------- Бизнес-логика ----------------

def create_attempt(db: Session, test_id: int, current_user: CurrentUser) -> Attempt:
    """
    Создать попытку прохождения теста.

    Правила:
    - тест должен быть активен
    - доступ по умолчанию: студент записан на курс ИЛИ преподаватель курса
      иначе: permission course:test:read
    - 1 активная попытка на (user_id, test_id) (если уже есть in_progress -> 400)
    - фиксируем список вопросов теста в attempt_questions (position + question_version_id)
    - создаём answers (value=-1) на каждый вопрос
    """
    test = _get_test_or_404(db, test_id)
    course = _get_course_or_404(db, test.course_id)

    if not test.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test is not active")

    default_allowed = _is_course_teacher(course, current_user) or _is_student_enrolled(db, course.id, current_user.id)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_READ,
        msg="You do not have access to this test",
    )

    existing_in_progress = (
        db.query(Attempt)
        .filter(
            Attempt.test_id == test.id,
            Attempt.user_id == current_user.id,
            Attempt.status == ATTEMPT_STATUS_IN_PROGRESS,
        )
        .first()
    )
    if existing_in_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active attempt for this test",
        )

    test_links = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == test.id)
        .order_by(TestQuestion.position.asc())
        .all()
    )
    if not test_links:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test has no questions")

    attempt = Attempt(
        user_id=current_user.id,
        test_id=test.id,
        status=ATTEMPT_STATUS_IN_PROGRESS,
        started_at=datetime.utcnow(),
        finished_at=None,
        score=None,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # фиксируем вопросы попытки + ответы
    for link in test_links:
        latest_qv = _get_latest_question_version_or_404(db, link.question_id)

        aq = AttemptQuestion(
            attempt_id=attempt.id,
            question_id=link.question_id,
            question_version_id=latest_qv.id,
            position=link.position,
        )
        db.add(aq)

        ans = Answer(
            attempt_id=attempt.id,
            question_id=link.question_id,
            question_version_id=latest_qv.id,
            value=-1,
        )
        db.add(ans)

    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(db: Session, attempt_id: int, current_user: CurrentUser) -> Attempt:
    """
    Получить попытку.

    default:
      - владелец попытки
      - преподаватель курса теста
    иначе:
      - permission test:answer:read
    """
    attempt = _get_attempt_or_404(db, attempt_id)
    test = _get_test_or_404(db, attempt.test_id)
    course = _get_course_or_404(db, test.course_id)

    default_allowed = (attempt.user_id == current_user.id) or _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.TEST_ANSWER_READ,
        msg="You do not have access to this attempt",
    )
    return attempt


def finish_attempt(db: Session, attempt_id: int, current_user: CurrentUser) -> Attempt:
    """
    Завершить попытку.
    - только владелец
    - если уже finished -> возвращаем как есть
    - считаем score = correct/total * 100
    """
    attempt = _get_attempt_or_404(db, attempt_id)

    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if attempt.status == ATTEMPT_STATUS_FINISHED:
        return attempt

    answers = db.query(Answer).filter(Answer.attempt_id == attempt.id).all()
    if not answers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attempt has no answers")

    total = len(answers)
    correct = 0

    for a in answers:
        qv = db.query(QuestionVersion).filter(QuestionVersion.id == a.question_version_id).first()
        if not qv:
            continue
        if a.value == qv.correct_index:
            correct += 1

    score = (Decimal(correct) / Decimal(total)) * Decimal("100")

    attempt.status = ATTEMPT_STATUS_FINISHED
    attempt.finished_at = datetime.utcnow()
    attempt.score = score

    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt
