from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.course import CourseRead, CourseListRead
from app.schemas.course_user import CourseUserRead
from app.services.course import (
    list_courses,
    _get_course_or_404,
    create_course,
    update_course,
    delete_course,
    list_course_tests,
    list_course_students,
    enroll_user_to_course,
    remove_user_from_course,
)

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=List[CourseListRead])
def api_list_courses(db: Session = Depends(get_db)):
    return list_courses(db)


@router.get("/{course_id}", response_model=CourseRead)
def api_get_course(course_id: int, db: Session = Depends(get_db)):
    return _get_course_or_404(db, course_id)


@router.post("/", response_model=CourseRead)
def api_create_course(
    title: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_course(db, current_user, title, description)


@router.patch("/{course_id}", response_model=CourseRead)
def api_update_course(
    course_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return update_course(db, course_id, current_user, title, description)


@router.delete("/{course_id}", response_model=CourseRead)
def api_delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return delete_course(db, course_id, current_user)


@router.get("/{course_id}/tests", response_model=List[dict])
def api_list_course_tests(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_course_tests(db, course_id, current_user)


@router.get("/{course_id}/students", response_model=List[CourseUserRead])
def api_list_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_course_students(db, course_id, current_user)


@router.post("/{course_id}/students", response_model=CourseUserRead)
def api_enroll_student(
    course_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return enroll_user_to_course(db, course_id, current_user, target_user_id=user_id)


@router.delete("/{course_id}/students/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_remove_student(
    course_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    remove_user_from_course(db, course_id, user_id, current_user)
