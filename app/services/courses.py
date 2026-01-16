from datetime import datetime
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.courses import Course
from app.models.course_users import CourseUser
from app.models.tests import Test
from app.core.security import CurrentUser
from app.core.permissions import Permissions
from app.schemas.course_user import CourseUserRead
from app.core.permissions import ensure_permission, ensure_default_or_permission
from app.services.notifications import create_notification

# ---------------- Вспомогательные функции ----------------

"""
Получить курс по ID.
Выбрасывает 404, если курс не найден или логически удалён.
"""
def _get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted == False).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


"""
Проверяет, является ли текущий пользователь преподавателем курса.
Возвращает True/False
"""
def _is_course_teacher(course: Course, user: CurrentUser) -> bool:
    return course.teacher_id == user.id


"""
Проверяет, записан ли пользователь на курс.
Возвращает True/False
"""
def _is_student_enrolled(course: Course, user: CurrentUser) -> bool:
    return any(link.user_id == user.id for link in course.students_links)


# ---------------- Бизнес-логика ----------------

"""
Получить список всех курсов
Доступ: всем
"""
def list_courses(db: Session) -> List[Course]:
    return db.query(Course).filter(Course.is_deleted == False).all()


"""
Создать новый курс
Доступ: permission 'course:add'
"""
def create_course(db: Session, current_user: CurrentUser, title: str, description: str) -> Course:
    ensure_permission(
        current_user.permissions,
        Permissions.COURSE_ADD,
        "You do not have permission to create courses",
        user_roles=current_user.roles,
    )
    course = Course(title=title, description=description, teacher_id=current_user.id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


"""
Обновить курс (название/описание)
Доступ:
  - по умолчанию: преподаватель курса
  - permission: 'course:info:write' для других пользователей
"""
def update_course(db: Session, course_id: int, current_user: CurrentUser, title: str | None, description: str | None) -> Course:
    course = _get_course_or_404(db, course_id)
    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_INFO_WRITE,
        user_roles=current_user.roles,
    )

    if title:
        course.title = title
    if description:
        course.description = description

    db.commit()
    db.refresh(course)
    return course


"""
Логическое удаление курса
Доступ:
  - по умолчанию: преподаватель курса
  - permission: 'course:del' для других пользователей
"""
def delete_course(db: Session, course_id: int, current_user: CurrentUser) -> Course:
    course = _get_course_or_404(db, course_id)
    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_DEL,
        user_roles=current_user.roles,
    )

    course.is_deleted = True
    db.commit()
    db.refresh(course)
    return course


"""
Получить список тестов курса
Доступ:
  - по умолчанию: преподаватель курса или студент на курсе
  - permission: 'course:testList' для остальных
"""
def list_course_tests(db: Session, course_id: int, current_user: CurrentUser,) -> list[Test]:
    course = _get_course_or_404(db, course_id)
    default_allowed = (
        _is_course_teacher(course, current_user)
        or _is_student_enrolled(course, current_user)
    )
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_TESTLIST,
        user_roles=current_user.roles,
    )

    return (
        db.query(Test)
        .filter(
            Test.course_id == course_id,
            Test.is_deleted == False,
        )
        .all()
    )


"""
Получить список студентов курса
Доступ:
  - по умолчанию: преподаватель курса
  - permission: 'course:userList' для остальных
"""
def list_course_students(db: Session, course_id: int, current_user: CurrentUser) -> List[CourseUser]:
    course = _get_course_or_404(db, course_id)
    default_allowed = _is_course_teacher(course, current_user)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_USERLIST,
        user_roles=current_user.roles,
    )
    return course.students_links


"""
Записать пользователя на курс
Доступ:
  - по умолчанию: пользователь может записать себя
  - permission: 'course:user:add' для записи других
"""
def enroll_user_to_course(db: Session, course_id: int, current_user: CurrentUser, target_user_id: int | None = None) -> CourseUser:
    course = _get_course_or_404(db, course_id)
    target_user_id = target_user_id or current_user.id
    default_allowed = target_user_id == current_user.id
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_USER_ADD,
        user_roles=current_user.roles,
    )

    existing = db.query(CourseUser).filter_by(course_id=course_id, user_id=target_user_id).first()
    if existing:
        return existing

    link = CourseUser(course_id=course_id, user_id=target_user_id, enrolled_at=datetime.utcnow())
    db.add(link)
    db.commit()
    create_notification(
        db,
        user_id=current_user.id,
        message=f"Вы записаны на курс «{course.title}».",
        payload={"type": "course_enroll", "course_id": course.id},
    )

    db.refresh(link)
    return link


"""
Удалить пользователя с курса
Доступ:
  - по умолчанию: пользователь может удалить себя
  - permission: 'course:user:del' для удаления других
"""
def remove_user_from_course(db: Session, course_id: int, user_id: int, current_user: CurrentUser) -> None:
    course = _get_course_or_404(db, course_id)
    default_allowed = user_id == current_user.id
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.COURSE_USER_DEL,
        user_roles=current_user.roles,
    )

    link = db.query(CourseUser).filter_by(course_id=course_id, user_id=user_id).first()
    if link:
        db.delete(link)
        create_notification(
            db,
            user_id=user_id,
            message=f"Вы удалены с курса «{course.title}».",
            payload={"type": "course_unenroll", "course_id": course.id},
        )
        db.commit()
