from fastapi import HTTPException

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
    
   

def require_permission(user, permission: str):
    if user.blocked:
        raise HTTPException(status_code=418, detail="User is blocked")
    if permission not in user.permissions:
        raise HTTPException(status_code=403, detail="Forbidden")


def require_self_or_permission(user, target_user_id: int, permission: str):
    if user.blocked:
        raise HTTPException(status_code=418, detail="User is blocked")
    if target_user_id == user.id:
        return
    if permission not in user.permissions:
        raise HTTPException(status_code=403, detail="Forbidden")