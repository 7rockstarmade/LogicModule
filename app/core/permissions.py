from fastapi import HTTPException, status
from typing import Iterable, Mapping

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
    

ALL_PERMISSIONS = {
    Permissions.USER_LIST_READ,
    Permissions.USER_FULLNAME_WRITE,
    Permissions.USER_DATA_READ,
    Permissions.USER_ROLES_READ,
    Permissions.USER_ROLES_WRITE,
    Permissions.USER_BLOCK_READ,
    Permissions.USER_BLOCK_WRITE,
    Permissions.COURSE_INFO_WRITE,
    Permissions.COURSE_TESTLIST,
    Permissions.COURSE_TEST_READ,
    Permissions.COURSE_TEST_WRITE,
    Permissions.COURSE_TEST_ADD,
    Permissions.COURSE_TEST_DEL,
    Permissions.COURSE_USERLIST,
    Permissions.COURSE_USER_ADD,
    Permissions.COURSE_USER_DEL,
    Permissions.COURSE_ADD,
    Permissions.COURSE_DEL,
    Permissions.QUEST_LIST_READ,
    Permissions.QUEST_READ,
    Permissions.QUEST_UPDATE,
    Permissions.QUEST_CREATE,
    Permissions.QUEST_DEL,
    Permissions.TEST_QUEST_DEL,
    Permissions.TEST_QUEST_ADD,
    Permissions.TEST_QUEST_UPDATE,
    Permissions.TEST_ANSWER_READ,
    Permissions.ANSWER_READ,
    Permissions.ANSWER_UPDATE,
    Permissions.ANSWER_DEL,
}

ROLE_PERMISSIONS: Mapping[str, set[str]] = {
    "admin": set(ALL_PERMISSIONS),
    "teacher": {
        Permissions.USER_LIST_READ,
        Permissions.USER_DATA_READ,
        Permissions.USER_ROLES_READ,
        Permissions.COURSE_INFO_WRITE,
        Permissions.COURSE_TESTLIST,
        Permissions.COURSE_TEST_READ,
        Permissions.COURSE_TEST_WRITE,
        Permissions.COURSE_TEST_ADD,
        Permissions.COURSE_TEST_DEL,
        Permissions.COURSE_USERLIST,
        Permissions.COURSE_USER_ADD,
        Permissions.COURSE_USER_DEL,
        Permissions.COURSE_ADD,
        Permissions.QUEST_LIST_READ,
        Permissions.QUEST_READ,
        Permissions.QUEST_UPDATE,
        Permissions.QUEST_CREATE,
        Permissions.QUEST_DEL,
        Permissions.TEST_QUEST_DEL,
        Permissions.TEST_QUEST_ADD,
        Permissions.TEST_QUEST_UPDATE,
        Permissions.TEST_ANSWER_READ,
        Permissions.ANSWER_READ,
        Permissions.ANSWER_UPDATE,
        Permissions.ANSWER_DEL,
    },
    "student": {
        Permissions.COURSE_TESTLIST,
        Permissions.COURSE_TEST_READ,
        Permissions.QUEST_LIST_READ,
        Permissions.QUEST_READ,
        Permissions.TEST_ANSWER_READ,
        Permissions.ANSWER_READ,
    },
}

class PermissionError(HTTPException):
    """Специальная ошибка для отказа в доступе."""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def has_permission(
    user_permissions: Iterable[str],
    permission: str,
    user_roles: Iterable[str] | None = None,
) -> bool:
    user_permissions = set(user_permissions or [])
    user_roles = list(user_roles or [])
    if permission in user_permissions:
        return True
    for role in user_roles:
        if permission in ROLE_PERMISSIONS.get(role, set()):
            return True
    return False


def ensure_permission(
    user_permissions: Iterable[str],
    permission: str,
    msg: str | None = None,
    user_roles: Iterable[str] | None = None,
) -> None:
    """Бросит 403, если у пользователя нет нужного permission."""
    if not has_permission(user_permissions, permission, user_roles):
        raise PermissionError(detail=msg or f"Missing permission: {permission}")


def ensure_default_or_permission(
    default_allowed: bool,
    user_permissions: Iterable[str],
    permission: str,
    msg: str | None = None,
    user_roles: Iterable[str] | None = None,
) -> None:
    """
    Если default_allowed == True — доступ есть по умолчанию.
    Если False — нужно наличие permission, иначе 403.
    """
    if default_allowed:
        return
    if not has_permission(user_permissions, permission, user_roles):
        raise PermissionError(detail=msg or f"Missing permission: {permission}")
