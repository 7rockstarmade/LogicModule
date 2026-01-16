from __future__ import annotations

from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.permissions import Permissions, ensure_permission, ensure_default_or_permission
from app.core.security import CurrentUser

from app.models.courses import Course
from app.models.course_users import CourseUser
from app.models.tests import Test
from app.models.test_questions import TestQuestion
from app.models.questions import Question
from app.models.question_versions import QuestionVersion
from app.models.attempts import Attempt
from app.models.answers import Answer
from app.models.users import User
from app.services.notifications import create_notification
from app.models.course_users import CourseUser



ATTEMPT_STATUS_FINISHED = "finished"

def _get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted == False).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


def _get_test_or_404(db: Session, test_id: int) -> Test:
    test = db.query(Test).filter(Test.id == test_id, Test.is_deleted == False).first()
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    return test


def _get_test_in_course_or_404(db: Session, course_id: int, test_id: int) -> Test:
    test = (
        db.query(Test)
        .filter(
            Test.id == test_id,
            Test.course_id == course_id,
            Test.is_deleted == False,
        )
        .first()
    )
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found in this course")
    return test


def _get_question_or_404(db: Session, question_id: int) -> Question:
    q = db.query(Question).filter(Question.id == question_id, Question.is_deleted == False).first()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return q


def _is_course_teacher(course: Course, current_user: CurrentUser) -> bool:
    return course.teacher_id == current_user.id


def _is_student_enrolled(db: Session, course_id: int, user_id: int) -> bool:
    return (
        db.query(CourseUser)
        .filter(CourseUser.course_id == course_id, CourseUser.user_id == user_id)
        .first()
        is not None
    )


def _ensure_test_not_locked_by_attempts(db: Session, test_id: int) -> None:
    """
    Запрет редактировать состав/порядок теста, если уже есть попытки.
    """
    any_attempt = db.query(Attempt).filter(Attempt.test_id == test_id).first()
    if any_attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is locked because attempts already exist",
        )



def create_test(db: Session, course_id: int, title: str, is_active: bool, current_user: CurrentUser) -> Test:
    course = _get_course_or_404(db, course_id)
    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_ADD,
        msg="You do not have permission to create tests",
        user_roles=current_user.roles,
    )

    test = Test(course_id=course_id, title=title, is_active=is_active, is_deleted=False)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


def delete_test(db: Session, course_id: int, test_id: int, current_user: CurrentUser) -> Test:
    course = _get_course_or_404(db, course_id)
    test = _get_test_in_course_or_404(db, course_id, test_id)

    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_DEL,
        msg="You do not have permission to delete tests",
        user_roles=current_user.roles,
    )

    test.is_deleted = True
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


def get_test_active_status(db: Session, course_id: int, test_id: int, current_user: CurrentUser) -> Dict[str, bool]:
    course = _get_course_or_404(db, course_id)
    test = _get_test_in_course_or_404(db, course_id, test_id)

    default_allowed = _is_course_teacher(course, current_user) or _is_student_enrolled(db, course_id, current_user.id)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_READ,
        msg="You do not have access to this test",
        user_roles=current_user.roles,
    )

    return {"is_active": bool(test.is_active)}


def set_test_active_status(db: Session, course_id: int, test_id: int, current_user: CurrentUser, is_active: bool) -> Test:
    course = _get_course_or_404(db, course_id)
    test = _get_test_in_course_or_404(db, course_id, test_id)

    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_WRITE,
        msg="You do not have permission to change test active status",
        user_roles=current_user.roles,
    )

    test.is_active = is_active
    if not is_active:
        in_progress = (
            db.query(Attempt)
            .filter(Attempt.test_id == test.id, Attempt.status != ATTEMPT_STATUS_FINISHED)
            .all()
        )
        for a in in_progress:
            a.status = ATTEMPT_STATUS_FINISHED
            db.add(a)

    if is_active:
        students = db.query(CourseUser).filter(CourseUser.course_id == course.id).all()
        for s in students:
            create_notification(
                db,
                user_id=s.user_id,
                message=f"Тест «{test.title}» активирован и доступен для прохождения.",
                payload={"type": "test_active", "course_id": course.id, "test_id": test.id},
            )


    db.add(test)
    db.commit()
    db.refresh(test)
    return test


def add_question_to_test(db: Session, test_id: int, question_id: int, current_user: CurrentUser) -> TestQuestion:
    test = _get_test_or_404(db, test_id)
    course = _get_course_or_404(db, test.course_id)
    question = _get_question_or_404(db, question_id)

    _ensure_test_not_locked_by_attempts(db, test.id)

    # default: преподаватель курса И автор вопроса
    default_allowed = _is_course_teacher(course, current_user) and (question.author_id == current_user.id)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.TEST_QUEST_ADD,
        msg="You do not have permission to add questions to test",
        user_roles=current_user.roles,
    )

    exists = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == test.id, TestQuestion.question_id == question.id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question already added to test")

    last_pos = (
        db.query(func.max(TestQuestion.position))
        .filter(TestQuestion.test_id == test.id)
        .scalar()
    )
    next_pos = (last_pos + 1) if last_pos is not None else 0

    link = TestQuestion(test_id=test.id, question_id=question.id, position=next_pos)
    db.add(link)
    db.commit()
    return link


def remove_question_from_test(db: Session, test_id: int, question_id: int, current_user: CurrentUser) -> None:
    test = _get_test_or_404(db, test_id)
    course = _get_course_or_404(db, test.course_id)

    _ensure_test_not_locked_by_attempts(db, test.id)

    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.TEST_QUEST_DEL,
        msg="You do not have permission to remove questions from test",
        user_roles=current_user.roles,
    )

    link = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == test.id, TestQuestion.question_id == question_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question is not in this test")

    db.delete(link)
    db.commit()

    # нормализуем позиции после удаления (0..n-1)
    links = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == test.id)
        .order_by(TestQuestion.position.asc())
        .all()
    )
    for i, l in enumerate(links):
        l.position = i
        db.add(l)
    db.commit()


def reorder_test_questions(db: Session, test_id: int, question_ids: List[int], current_user: CurrentUser) -> List[TestQuestion]:
    test = _get_test_or_404(db, test_id)
    course = _get_course_or_404(db, test.course_id)

    _ensure_test_not_locked_by_attempts(db, test.id)

    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.TEST_QUEST_UPDATE,
        msg="You do not have permission to reorder questions",
        user_roles=current_user.roles,
    )

    existing = (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == test.id)
        .all()
    )
    if not existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test has no questions")

    existing_ids = {x.question_id for x in existing}
    new_ids = list(question_ids)

    if set(new_ids) != existing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="question_ids must contain exactly the same set of questions as in the test",
        )

    # обновляем позиции
    pos_by_id = {qid: i for i, qid in enumerate(new_ids)}
    for link in existing:
        link.position = pos_by_id[link.question_id]
        db.add(link)

    db.commit()

    return (
        db.query(TestQuestion)
        .filter(TestQuestion.test_id == test.id)
        .order_by(TestQuestion.position.asc())
        .all()
    )


# ---------------- NEW: (3.8 - 3.10) results ----------------

def list_test_result_users(db: Session, test_id: int, current_user: CurrentUser) -> List[User]:
    """
    Пользователи, прошедшие тест (есть finished attempts).
    default: преподаватель курса
    permission: test:answer:read
    """
    test = _get_test_or_404(db, test_id)
    course = _get_course_or_404(db, test.course_id)

    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.TEST_ANSWER_READ,
        msg="You do not have permission to read test results",
        user_roles=current_user.roles,
    )

    user_ids = (
        db.query(Attempt.user_id)
        .filter(Attempt.test_id == test.id, Attempt.status == ATTEMPT_STATUS_FINISHED)
        .distinct()
        .all()
    )
    ids = [x[0] for x in user_ids]
    if not ids:
        return []

    return db.query(User).filter(User.id.in_(ids)).all()


def list_test_grades(db: Session, test_id: int, current_user: CurrentUser, user_id: Optional[int]) -> List[Attempt]:
    """
    Оценки пользователей (finished attempts).
    default:
      - преподаватель курса: всех
      - пользователь: только себя (user_id=None или user_id==self)
    permission:
      - test:answer:read
    """
    test = _get_test_or_404(db, test_id)
    course = _get_course_or_404(db, test.course_id)

    is_teacher = _is_course_teacher(course, current_user)
    is_self = (user_id is None) or (user_id == current_user.id)

    default_allowed = is_teacher or is_self
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.TEST_ANSWER_READ,
        msg="You do not have permission to read grades",
        user_roles=current_user.roles,
    )

    q = db.query(Attempt).filter(Attempt.test_id == test.id, Attempt.status == ATTEMPT_STATUS_FINISHED)
    if user_id is not None:
        q = q.filter(Attempt.user_id == user_id)

    return q.order_by(Attempt.finished_at.desc()).all()


def list_test_answers(db: Session, test_id: int, current_user: CurrentUser, user_id: Optional[int]) -> List[dict]:
    """
    Ответы пользователей по тесту.
    default:
      - преподаватель: любых
      - пользователь: только себя
    permission:
      - test:answer:read
    Возвращаем "attempt -> answers" (чтобы фронту удобно).
    """
    test = _get_test_or_404(db, test_id)
    course = _get_course_or_404(db, test.course_id)

    is_teacher = _is_course_teacher(course, current_user)
    is_self = (user_id is None) or (user_id == current_user.id)

    default_allowed = is_teacher or is_self
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.TEST_ANSWER_READ,
        msg="You do not have permission to read answers",
        user_roles=current_user.roles,
    )

    attempts_q = (
        db.query(Attempt)
        .filter(Attempt.test_id == test.id, Attempt.status == ATTEMPT_STATUS_FINISHED)
        .order_by(Attempt.finished_at.desc())
    )
    if user_id is not None:
        attempts_q = attempts_q.filter(Attempt.user_id == user_id)

    attempts = attempts_q.all()
    if not attempts:
        return []

    result = []
    for a in attempts:
        answers = db.query(Answer).filter(Answer.attempt_id == a.id).all()

        # подтягиваем correct_index из зафиксированной версии
        version_ids = [x.question_version_id for x in answers]
        versions = db.query(QuestionVersion).filter(QuestionVersion.id.in_(version_ids)).all()
        correct_map = {v.id: v.correct_index for v in versions}

        items = []
        for ans in answers:
            correct_index = correct_map.get(ans.question_version_id, -999999)
            is_correct = (ans.value == correct_index)
            items.append(
                {
                    "answer_id": ans.id,
                    "question_id": ans.question_id,
                    "question_version_id": ans.question_version_id,
                    "value": ans.value,
                    "correct_index": correct_index,
                    "is_correct": is_correct,
                }
            )

        result.append(
            {
                "attempt_id": a.id,
                "user_id": a.user_id,
                "finished_at": a.finished_at,
                "score": a.score,
                "answers": items,
            }
        )

    return result
