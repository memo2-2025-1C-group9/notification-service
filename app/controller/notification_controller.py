from app.repositories.queue_repository import QueueRepository
from app.schemas.notification_schemas import (
    UserNotificationEvent,
    CourseNotificationEvent,
)
import logging


def handle_add_queue_message(
    notification: UserNotificationEvent | CourseNotificationEvent,
):
    try:
        queue_repo = QueueRepository()
        # TODO: model dump con nones/exlude buscarlo
        success = queue_repo.send_message(notification.model_dump(exclude_none=True))

        # TODO: Los returns de aca
        if success:
            return {"message": "Notificación enviada correctamente a la queue"}
        else:
            return {"message": "Error al enviar la notificación a la queue"}

    except Exception as e:
        logging.error(f"Error al procesar la notificación: {str(e)}")
        raise
