from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel


SECRET_KEY = "key123123123"
ALGORITHM = "HS256"

auth_scheme = HTTPBearer()


class TokenPayload(BaseModel):
    sub: int
    fullName: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    blocked: bool = False


class CurrentUser(BaseModel):
    id: int
    full_name: Optional[str] = None
    permissions: List[str] = []
    blocked: bool = False


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )

    try:
        token_data = TokenPayload(**payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )

    return token_data


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> CurrentUser:
    token = credentials.credentials
    token_data = decode_access_token(token)

    user = CurrentUser(
        id=token_data.sub,
        full_name=token_data.fullName,
        permissions=token_data.permissions,
        blocked=token_data.blocked,
    )

    if user.blocked:
        raise HTTPException(
            status_code=418,
            detail="User is blocked",
        )
    return user


def get_current_active_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.blocked:
        raise HTTPException(
            status_code=418,
            detail="User is blocked",
        )
    return current_user