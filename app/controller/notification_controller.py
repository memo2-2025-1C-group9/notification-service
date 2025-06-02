from app.repositories.queue_repository import QueueRepository
from app.schemas.notification_schemas import (
    UserNotificationEvent,
    CourseNotificationEvent,
)


def handle_add_queue_message(
    notification: UserNotificationEvent | CourseNotificationEvent,
):
    queue_repo = QueueRepository()
    return queue_repo.send_message(notification.model_dump(exclude_none=True))
