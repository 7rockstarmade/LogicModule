from fastapi import HTTPException, status
from typing import Iterable

class Permissions:
    USER_LIST_READ      = "user:list:read"
    USER_FULLNAME_WRITE = "user:fullName:write"
    USER_DATA_READ      = "user:data:read"
    USER_ROLES_READ     = "user:roles:read"
    USER_ROLES_WRITE    = "user:roles:write"
    USER_BLOCK_READ     = "user:block:read"
    USER_BLOCK_WRITE    = "user:block:write"

    COURSE_INFO_WRITE   = "course:info:write"
    COURSE_TESTLIST     = "course:testList"
    COURSE_TEST_READ    = "course:test:read"
    COURSE_TEST_WRITE   = "course:test:write"
    COURSE_TEST_ADD     = "course:test:add"
    COURSE_TEST_DEL     = "course:test:del"
    COURSE_USERLIST     = "course:userList"
    COURSE_USER_ADD     = "course:user:add"
    COURSE_USER_DEL     = "course:user:del"
    COURSE_ADD          = "course:add"
    COURSE_DEL          = "course:del"

    QUEST_LIST_READ     = "quest:list:read"
    QUEST_READ          = "quest:read"
    QUEST_UPDATE        = "quest:update"
    QUEST_CREATE        = "quest:create"
    QUEST_DEL           = "quest:del"

    TEST_QUEST_DEL      = "test:quest:del"
    TEST_QUEST_ADD      = "test:quest:add"
    TEST_QUEST_UPDATE   = "test:quest:update"
    TEST_ANSWER_READ    = "test:answer:read"

    ANSWER_READ         = "answer:read"
    ANSWER_UPDATE       = "answer:update"
    ANSWER_DEL          = "answer:del"
    
   
class PermissionError(HTTPException):
    """Специальная ошибка для отказа в доступе."""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def has_permission(user_permissions: Iterable[str], permission: str) -> bool:
    return permission in user_permissions


def ensure_permission(user_permissions: Iterable[str], permission: str, msg: str | None = None) -> None:
    """Бросит 403, если у пользователя нет нужного permission."""
    if permission not in user_permissions:
        raise PermissionError(detail=msg or f"Missing permission: {permission}")


def ensure_default_or_permission(
    default_allowed: bool,
    user_permissions: Iterable[str],
    permission: str,
    msg: str | None = None,
) -> None:
    """
    Если default_allowed == True — доступ есть по умолчанию.
    Если False — нужно наличие permission, иначе 403.
    """
    if default_allowed:
        return
    if permission not in user_permissions:
        raise PermissionError(detail=msg or f"Missing permission: {permission}")