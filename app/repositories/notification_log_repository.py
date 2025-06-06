from sqlalchemy.orm import Session
from app.models.notification_log import NotificationLog
from typing import List


def create_log(
    db: Session,
    user_id: int,
    notification_type: str,
    event: str,
    method: str,
    subject: str,
    body: str,
) -> NotificationLog:
    log = NotificationLog(
        user_id=user_id,
        notification_type=notification_type,
        event=event,
        method=method,
        subject=subject,
        body=body,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_user_logs_by_id(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[NotificationLog]:
    return (
        db.query(NotificationLog)
        .filter(NotificationLog.user_id == user_id)
        .order_by(NotificationLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
