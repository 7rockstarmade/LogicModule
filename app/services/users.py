from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.attempts import Attempt
from app.models.course_users import CourseUser
from app.models.users import User
from app.schemas.user import UserCreate, UserRead, UserBase
from app.core.security import CurrentUser
from app.core.permissions import ensure_permission, ensure_default_or_permission
from app.core.permissions import *


"""
Получить пользователя из БД
Вспомогательная-private функция
"""
def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


"""
Получить список всех пользователей
Доступ:
  - permission: user:list:read
"""
def list_users(db: Session, current_user: CurrentUser) -> list[User]:
    # Проверка разрешения на просмотр списка пользователей
    ensure_permission(
        current_user.permissions,
        Permissions.USER_LIST_READ, 
        "You do not have permission to list users",
        user_roles=current_user.roles,
    )
    return db.query(User).all()


# Получение информации о пользователе (ФИО)
def get_user_basic_info(db: Session, current_user: CurrentUser, user_id: int) -> User:
    """
    Получить информацию о пользователе (ФИО).
    Доступ:
      + о себе
      + о другом
    """
    user = _get_user_or_404(db, user_id)
    return user


def get_user_data(db: Session, user_id: int, current_user: CurrentUser) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    default_allowed = (user_id == current_user.id)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.USER_DATA_READ,
        msg="You do not have permission to read this user's data",
        user_roles=current_user.roles,
    )

    courses_count = (
        db.query(func.count())
        .select_from(CourseUser)
        .filter(CourseUser.user_id == user_id)
        .scalar()
    ) or 0

    attempts_count = (
        db.query(func.count())
        .select_from(Attempt)
        .filter(Attempt.user_id == user_id)
        .scalar()
    ) or 0

    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "is_blocked": current_user.is_blocked,
        "roles": list(user.roles or []),
        "courses_count": int(courses_count),
        "attempts_count": int(attempts_count),
    }

"""
Изменить ФИО пользователя.
Доступ:
  + Себе
  - Другому (нужен permission user:fullName:write)
"""
def update_user_full_name(db: Session, current_user: CurrentUser, user_id: int, new_full_name: str) -> User:
    is_self = current_user.id == user_id
    ensure_default_or_permission(
        is_self,
        current_user.permissions,
        Permissions.USER_FULLNAME_WRITE,
        "You do not have permission to update this user's full name",
        user_roles=current_user.roles,
    )
    user = _get_user_or_404(db, user_id)
    user.full_name = new_full_name
    db.commit()
    db.refresh(user)
    return user




def get_user_roles(db: Session, user_id: int, current_user: CurrentUser) -> list[str]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # default: только о себе, иначе нужна permission
    default_allowed = (user_id == current_user.id)
    ensure_default_or_permission(
        default_allowed,
        current_user.permissions,
        Permissions.USER_ROLES_READ,
        msg="You do not have permission to read roles",
        user_roles=current_user.roles,
    )

    return list(user.roles or [])


def set_user_roles(db: Session, user_id: int, roles: list[str], current_user: CurrentUser) -> list[str]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    ensure_permission(
        current_user.permissions,
        Permissions.USER_ROLES_WRITE,
        msg="You do not have permission to change roles",
        user_roles=current_user.roles,
    )

    clean = []
    seen = set()
    for r in roles:
        r = (r or "").strip()
        if not r or r in seen:
            continue
        seen.add(r)
        clean.append(r)

    user.roles = clean
    db.add(user)
    db.commit()
    db.refresh(user)
    return list(user.roles or [])



"""
Получить статус блокировки пользователя.
Доступ:
  - permission: user:block:read
"""
def get_user_block_status(db: Session, current_user: CurrentUser, user_id: int) -> bool:
    ensure_permission(
        current_user.permissions,
        Permissions.USER_BLOCK_READ,
        "You do not have permission to view block status",
        user_roles=current_user.roles,
    )
    user = _get_user_or_404(db, user_id)
    return user.is_blocked


"""
Заблокировать или разблокировать пользователя.
Доступ:
  - permission: user:block:write
"""
def set_user_block_status(db: Session, current_user: CurrentUser, user_id: int, blocked: bool) -> User:
    ensure_permission(
        current_user.permissions, 
        Permissions.USER_BLOCK_WRITE, 
        "You do not have permission to change block status",
        user_roles=current_user.roles,
    )
    
    user = _get_user_or_404(db, user_id)
    user.is_blocked = blocked
    db.commit()
    db.refresh(user)
    return user


"""
Запись пользователя.
Вызывается модулем логики при создании нового пользователя
"""
def create_user(db: Session, data: UserCreate, user_id: int) -> User:
    user = User(
        id=user_id,
        username=data.username,
        full_name=data.full_name,
        email=data.email,
        is_blocked=data.is_blocked,
        roles=list(data.roles or []),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with given id, username or email already exists"
        )

    db.refresh(user)
    return user
