from sqlalchemy.orm import Session
from app.schemas.notification_schemas import UserPreferences
from app.services.user_service import (
    validate_user,
    get_user,
    edit_user,
    get_user_logs,
)


async def handle_validate_user(token: str):
    return await validate_user(token)


def handle_get_user(db: Session, user_id: int):
    return get_user(db, user_id)


def handle_edit_user(db: Session, user_id: int, preferences: UserPreferences):
    return edit_user(db, user_id, preferences)


def handle_get_user_logs(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return get_user_logs(db, user_id, skip, limit)
