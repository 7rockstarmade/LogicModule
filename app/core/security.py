from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import List, Optional
from app.core.config import settings

auth_scheme = HTTPBearer()


class CurrentUser(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    roles: List[str] = []
    permissions: List[str] = []
    is_blocked: bool = False


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),) -> CurrentUser:
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    try:
        return CurrentUser(
            id=int(payload["sub"]),
            username=payload.get("username", ""),
            full_name=payload.get("fullName"),
            roles=payload.get("roles", []),
            email=payload.get("email"),
            permissions=payload.get("permissions", []),
            is_blocked=payload.get("blocked", False),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
