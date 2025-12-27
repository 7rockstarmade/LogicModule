from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.users import list_users, get_user_basic_info, update_user_full_name, create_user, get_user_roles, get_user_block_status
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserBase
from app.core.security import CurrentUser, get_current_user
from app.core.permissions import *

router = APIRouter(prefix="/users")

@router.get('/', response_model=list[UserRead])
def get_all_users(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    users = list_users(db=db, current_user=current_user)
    return users

@router.get('/{user_id}')
def get_user_by_id(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_info = get_user_basic_info(db=db, current_user=current_user, user_id=user_id)
    return user_info.full_name

@router.patch('/{user_id}/full-name', response_model=UserRead)
def change_user_full_name(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user = update_user_full_name(
        db=db, 
        current_user=current_user,
        user_id=user_id,
        new_full_name=user_in.full_name
        )
    return user


@router.get('/users/{user_id}/data')
def get_user_roles_by_id(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_roles = get_user_roles(
        db=db,
        current_user=current_user,
        user_id=user_id
    )
    return user_roles


@router.get('users/{user_id}/block')
def user_block_status(user_id: int, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user_block_status = get_user_block_status(
        db=db,
        current_user=current_user,
        user_id=user_id
    )
    return user_block_status


# ТЕСТОВЫЙ ЭНД-ПОИНТ
@router.post("/create_user")
def create_user_endpoint(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    data = UserBase(
        username=current_user.username,
        full_name=current_user.full_name,
        is_blocked=current_user.is_blocked
    )
    user = create_user(db, data)
    return user