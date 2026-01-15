from __future__ import annotations

from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session

from app.core.security import CurrentUser
from app.models.notifications import Notification


def create_notification(
    db: Session,
    user_id: int,
    message: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Notification:
    n = Notification(user_id=user_id, message=message, payload=payload)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def list_my_notifications(db: Session, current_user: CurrentUser) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.asc())
        .all()
    )


def clear_my_notifications(db: Session, current_user: CurrentUser) -> int:
    count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return int(count)
