from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.notification import NotificationRead
from app.services.notifications import list_my_notifications, clear_my_notifications

router = APIRouter(tags=["Notifications"])


@router.get("/notification", response_model=list[NotificationRead])
@router.get("/api/notification", response_model=list[NotificationRead])
def api_get_notifications(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_my_notifications(db, current_user)



@router.delete("/notification")
@router.delete("/api/notification")
def api_clear_notifications(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    deleted = clear_my_notifications(db, current_user)
    return {"deleted": deleted}
