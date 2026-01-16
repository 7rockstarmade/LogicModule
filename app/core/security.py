from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import List, Optional
from app.core.config import settings
from app.db.session import get_db
from app.models.users import User
from sqlalchemy.orm import Session

auth_scheme = HTTPBearer()


class CurrentUser(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    roles: List[str] = []
    permissions: List[str] = []
    is_blocked: bool = False


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    try:
        user_id = int(payload["sub"])
        db_user = db.query(User).filter(User.id == user_id).first()
        roles = list(db_user.roles or []) if db_user else payload.get("roles", [])
        is_blocked = bool(db_user.is_blocked) if db_user else payload.get("blocked", False)
        return CurrentUser(
            id=user_id,
            username=payload.get("username", ""),
            full_name=payload.get("fullName"),
            roles=roles,
            email=payload.get("email"),
            permissions=payload.get("permissions", []),
            is_blocked=is_blocked,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
