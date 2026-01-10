from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.tests import Test
from app.core.security import CurrentUser
from app.core.permissions import Permissions
from app.core.permissions import ensure_permission, ensure_default_or_permission
from app.services.courses import _get_course_or_404, _is_course_teacher, _is_student_enrolled

# ---------------- Вспомогательные функции ----------------

"""
Получить тест по ID в рамках курса.
404 — если не найден или удалён.
"""
def _get_test_or_404(db: Session, course_id: int, test_id: int) -> Test:
    test = (db.query(Test).filter(
            Test.id == test_id,
            Test.course_id == course_id,
            Test.is_deleted == False,
        ).first()
    )
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    return test


# ======================================================
# БИЗНЕС-ЛОГИКА ТЕСТОВ
# ======================================================

"""
Создать тест в курсе
Доступ:
  - по умолчанию: преподаватель курса
  - permission: course:test:add
"""
def create_test(
    db: Session,
    course_id: int,
    current_user: CurrentUser,
    title: str,
) -> Test:
    course = _get_course_or_404(db, course_id)

    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_ADD,
    )

    test = Test(
        course_id=course.id,
        title=title,
        is_active=False,
        is_deleted=False,
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


"""
Логически удалить тест
Доступ:
  - по умолчанию: преподаватель курса
  - permission: course:test:del
"""
def delete_test(
    db: Session,
    course_id: int,
    test_id: int,
    current_user: CurrentUser,
) -> Test:
    course = _get_course_or_404(db, course_id)
    test = _get_test_or_404(db, course_id, test_id)

    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_DEL,
    )

    test.is_deleted = True
    db.commit()
    db.refresh(test)
    return test


"""
Получить статус активности теста
Доступ:
  - по умолчанию: преподаватель курса или студент на курсе
  - permission: course:test:read
"""
def get_test_active_status(
    db: Session,
    course_id: int,
    test_id: int,
    current_user: CurrentUser,
) -> bool:
    course = _get_course_or_404(db, course_id)
    test = _get_test_or_404(db, course_id, test_id)

    default_allowed = (
        _is_course_teacher(course, current_user)
        or _is_student_enrolled(course, current_user)
    )
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_READ,
    )

    return test.is_active


"""
Изменить статус активности теста
Доступ:
  - по умолчанию: преподаватель курса
  - permission: course:test:write
"""
def set_test_active_status(
    db: Session,
    course_id: int,
    test_id: int,
    current_user: CurrentUser,
    is_active: bool,
) -> Test:
    course = _get_course_or_404(db, course_id)
    test = _get_test_or_404(db, course_id, test_id)

    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TEST_WRITE,
    )

    test.is_active = is_active
    db.commit()
    db.refresh(test)
    return test


# ======================================================
# ЗАГЛУШКИ ДЛЯ ВОПРОСОВ И РЕЗУЛЬТАТОВ
# (структура правильная, реализация позже)
# ======================================================

"""
Добавить вопрос в тест
"""
def add_question_to_test():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Question creation is not implemented yet",
    )


"""
Удалить вопрос из теста
"""
def remove_question_from_test():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Question deletion is not implemented yet",
    )


"""
Изменить порядок вопросов в тесте
"""
def update_questions_order():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Question ordering is not implemented yet",
    )


"""
Пользователи, прошедшие тест
"""
def list_test_result_users():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Test results are not implemented yet",
    )


"""
Оценки пользователей за тест
"""
def list_test_grades():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Grades are not implemented yet",
    )


"""
Ответы пользователей
"""
def list_test_answers():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Answers are not implemented yet",
    )
