from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.users import User
from app.schemas.user import UserCreate, UserRead, UserBase
from app.core.security import CurrentUser
from app.core.permissions import ensure_permission
from app.core.permissions import *


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Получение списка всех пользователей
def list_users(db: Session, current_user: CurrentUser) -> list[User]:
    """
    Получить список всех пользователей
    Доступ:
      - permission: user:list:read
    """
    # Проверка разрешения на просмотр списка пользователей
    ensure_permission(current_user.permissions, Permissions.USER_LIST_READ, "You do not have permission to list users")
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


# Изменение ФИО пользователя
def update_user_full_name(
    db: Session, current_user: CurrentUser, user_id: int, new_full_name: str
) -> User:
    """
    Изменить ФИО пользователя.
    Доступ:
      + Себе
      - Другому (нужен permission user:fullName:write)
    """
    is_self = current_user.id == user_id
    ensure_permission(
        current_user.permissions,
        Permissions.USER_FULLNAME_WRITE if not is_self else "",
        "You do not have permission to update this user's full name"
    )
    
    user = _get_user_or_404(db, user_id)
    user.full_name = new_full_name
    db.commit()
    db.refresh(user)
    return user


# Получение информации о пользователе (курсы, оценки, тесты)
def get_user_data():
    ...
    #потом доделаю


# Получение ролей пользователя
def get_user_roles(db: Session, current_user: CurrentUser, user_id: int) -> list[str]:
    """
    Получить роли пользователя.
    Доступ:
      - permission: user:roles:read
    """
    ensure_permission(current_user.permissions, Permissions.USER_ROLES_READ, "You do not have permission to view roles")

    # Если пользователь запрашивает свои роли, отдаем их из текущего токена
    if user_id == current_user.id:
        return current_user.roles

    # Заглушка на случай, если нужно получать роли других пользователей
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Fetching roles for other users is not implemented"
    )


# Блокировка/разблокировка пользователя
def get_user_block_status(db: Session, current_user: CurrentUser, user_id: int) -> bool:
    """
    Получить статус блокировки пользователя.
    Доступ:
      - permission: user:block:read
    """
    ensure_permission(current_user.permissions, Permissions.USER_BLOCK_READ, "You do not have permission to view block status")
    user = _get_user_or_404(db, user_id)
    return user.is_blocked


def set_user_block_status(
    db: Session, current_user: CurrentUser, user_id: int, blocked: bool
) -> User:
    """
    Заблокировать или разблокировать пользователя.
    Доступ:
      - permission: user:block:write
    """
    ensure_permission(current_user.permissions, Permissions.USER_BLOCK_WRITE, "You do not have permission to change block status")
    
    user = _get_user_or_404(db, user_id)
    user.is_blocked = blocked
    db.commit()
    db.refresh(user)
    return user


# Заглушка на изменение ролей
def update_user_roles(db: Session, current_user: CurrentUser, user_id: int, roles: list[str]) -> User:
    """
    Изменить роли пользователя.
    Заглушка, так как изменение ролей производится через отдельный модуль авторизации.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Role management is handled by the authorization module"
    )




#ТЕСТОВАЯ ФУНКЦИЯ
def create_user(db: Session, data: UserBase) -> User:
    user = User(
        username = data.username,
        full_name = data.full_name,
        is_blocked = data.is_blocked,
        
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user