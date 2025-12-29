from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.users import _list_users, _get_user_basic_info, _update_user_full_name, _get_user_roles, _get_user_block_status, _set_user_block_status, _create_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserBase
from app.core.security import CurrentUser, get_current_user
from app.core.permissions import *

router = APIRouter(prefix="/users")

""" 1.1 GET /users -> Получить список всех пользователей"""
@router.get('/', response_model=list[UserRead])
def get_all_users(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    users = _list_users(db=db, current_user=current_user)
    return users

""" 1.2 GET /users/{user_id} -> Получить пользователя по ID"""
@router.get('/{user_id}')
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_info = _get_user_basic_info(db=db, current_user=current_user, user_id=user_id)
    return user_info.full_name

""" 1.3 PATCH /users/{user_id}/full-name -> Изменить имя пользователя по ID"""
@router.patch('/{user_id}/full-name', response_model=UserRead)
def change_user_full_name(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user = _update_user_full_name(
        db=db, 
        current_user=current_user,
        user_id=user_id,
        new_full_name=user_in.full_name
        )
    return user

""" 1.4 GET /users/{user_id}/data -> Получить роли пользователя по ID"""
@router.get('/{user_id}/data')
def get_user_data_by_id():
    ... 
    """В разработке"""

""" 1.5 GET /users/{user_id}/roles -> Получить роли пользователя по ID"""
@router.get('/{user_id}/roles')
def get_user_roles(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_roles = _get_user_roles(
        db=db,
        current_user=current_user,
        user_id=user_id
    )
    return user_roles

""" 1.6 PUT /users/{user_id}/roles -> Изменить роли пользователя по ID"""
@router.put('/{user_id}/roles')
def set_user_roles():
    ...
    """В разработке"""

""" 1.7 GET /users/{user_id}/block -> Получить статус блокировки пользователя по ID"""
@router.get('/{user_id}/block')
def get_user_block_status(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_block_status = _get_user_block_status(
        db=db,
        current_user=current_user,
        user_id=user_id
    )
    return user_block_status

""" 1.8 PUT /users/{user_id}/block -> Изменить статус блокировки пользователя по ID"""
@router.post('/{user_id}/block')
def set_user_block_status(user_id: int, user_in: UserUpdate ,db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user = _set_user_block_status(
        db=db,
        current_user=current_user,
        user_id=user_id,
        blocked=user_in.is_blocked
    )
    return user

""" POST /users/create_user -> Запись пользователя в БД, вызывается модулем авторизации"""
@router.post("/create_user")
def create_user(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    data = UserCreate(
        username=current_user.username,
        full_name=current_user.full_name,
        is_blocked=current_user.is_blocked
    )
    user = _create_user(db, data, current_user.id)
    return user