from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserDataRead, UserRead, UserUpdate, UserBase, UserMeRead, UserRolesUpdate
from app.core.security import CurrentUser, get_current_user
from app.core.permissions import *

from app.services.users import (
    get_user_data,
    list_users,
    get_user_basic_info,
    update_user_full_name,
    get_user_roles,
    get_user_block_status,
    set_user_block_status,
    create_user,
    set_user_roles,
)

router = APIRouter(prefix="/api/users", tags=["Users"])

""" 0.1 GET /users/me -> Получить данные о себе"""
@router.get('/me', response_model=UserMeRead)
def api_get_me(current_user: CurrentUser = Depends(get_current_user)):
    return {"id": current_user.id, "full_name": current_user.full_name}

""" 1.1 GET /users -> Получить список всех пользователей"""
@router.get('/', response_model=list[UserRead])
def api_get_all_users(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    users = list_users(db=db, current_user=current_user)
    return users

""" 1.2 GET /users/{user_id} -> Получить пользователя по ID"""
@router.get('/{user_id}')
def api_get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_info = get_user_basic_info(db=db, current_user=current_user, user_id=user_id)
    return user_info.full_name

""" 1.3 PATCH /users/{user_id}/full-name -> Изменить имя пользователя по ID"""
@router.patch('/{user_id}/full-name', response_model=UserRead)
def api_change_user_full_name(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user = update_user_full_name(
        db=db, 
        current_user=current_user,
        user_id=user_id,
        new_full_name=user_in.full_name
        )
    return user

""" 1.4 GET /users/{user_id}/data -> Получить всю информацию о пользователе по ID"""
@router.get("/{user_id}/data", response_model=UserDataRead)
def api_get_user_data(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return get_user_data(db, user_id, current_user)


""" 1.5 GET /users/{user_id}/roles -> Получить роли пользователя по ID"""
@router.get('/{user_id}/roles')
def api_get_user_roles(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_roles = get_user_roles(
        db=db,
        current_user=current_user,
        user_id=user_id
    )
    return user_roles

""" 1.6 PUT /users/{user_id}/roles -> Изменить роли пользователя по ID"""
@router.put('/{user_id}/roles')
def api_set_user_roles(
    user_id: int,
    user_in: UserRolesUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return set_user_roles(
        db=db,
        user_id=user_id,
        roles=user_in.roles,
        current_user=current_user,
    )

""" 1.7 GET /users/{user_id}/block -> Получить статус блокировки пользователя по ID"""
@router.get('/{user_id}/block')
def api_get_user_block_status(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_block_status = get_user_block_status(
        db=db,
        current_user=current_user,
        user_id=user_id
    )
    return user_block_status

""" 1.8 PUT /users/{user_id}/block -> Изменить статус блокировки пользователя по ID"""
@router.post('/{user_id}/block')
def api_set_user_block_status(user_id: int, user_in: UserUpdate ,db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user = set_user_block_status(
        db=db,
        current_user=current_user,
        user_id=user_id,
        blocked=user_in.is_blocked
    )
    return user

""" POST /users/create_user -> Запись пользователя в БД, вызывается модулем авторизации"""
@router.post("/create_user")
def api_create_user(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    data = UserCreate(
        username=current_user.username,
        full_name=current_user.full_name,
        is_blocked=current_user.is_blocked,
        email=current_user.email,
        roles=current_user.roles,
    )
    user = create_user(db, data, current_user.id)
    return user
