# La idea es la siguiente:
# 1. El worker va a estar escuchando en la queue
# 2. Va a recibir el mensaje
#       y tengo que tener la manera de saber:
#            Que tipo de mensaje es
#            El email y tokenFMC del usuario (El token lo voy a tener en la base de datos)
#            Y las preferencias del usuario en cuanto a que tipo de notificaciones quiere recibir segun el evento

from app.schemas.notification_schemas import (
    UserNotificationEvent,
    CourseNotificationEvent,
)
from app.repositories.user_repository import get_user_by_id, create_user
from app.services.email_notification import send_email
from app.utils.notification_formatter import format_notification
from app.db.session import SessionLocal
import json
import logging


def process_message(body: bytes):
    try:
        # Decodificar el mensaje de bytes a string
        message_str = body.decode("utf-8")
        message_dict = json.loads(message_str)

        # Determinar el tipo de mensaje basado en las claves presentes
        if "id_user" in message_dict:
            notification = UserNotificationEvent(**message_dict)
            process_user_notification(notification)
        elif "id_course" in message_dict:
            notification = CourseNotificationEvent(**message_dict)
            # process_course_notification(notification)
        else:  # No deberia entrar nunca aca, se valida el formato con el endpoint de la API
            logging.error(f"Mensaje con formato inválido: {message_dict}")
            raise ValueError("Formato de mensaje no reconocido")

    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar el mensaje JSON: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Error al procesar el mensaje: {str(e)}")
        raise


def process_user_notification(notification: UserNotificationEvent):
    db = None
    try:
        logging.info(
            f"Procesando notificación de usuario: {notification.id_user}, tipo: {notification.notification_type}, evento: {notification.event}"
        )
        # Obtener las preferencias del usuario
        db = SessionLocal()

        user_id = notification.id_user

        user = get_user_by_id(db, user_id)
        if not user:  # Usuario no registrado, crearlo con valores default
            logging.info(f"Usuario no registrado, creando usuario con ID: {user_id}")
            user = create_user(db, user_id)

        # subject, body = format_notification(  # TODO: Funcion a chequear
        #    notification.notification_type, notification.event, notification.data
        # )
        # Procesar según el tipo de evento
        if should_notify(user, notification.notification_type, "email"):
            logging.info(
                f"Procesando notificación de {notification.notification_type} EMAIL para usuario {notification.id_user}"
            )
            # send_email(notification.email, subject, body)

        if should_notify(user, notification.notification_type, "push"):
            # TODO: Implementar lógica para notificación de calificación
            logging.info(
                f"Procesando notificación de {notification.notification_type} PUSH para usuario {notification.id_user}"
            )

    except Exception as e:
        logging.error(f"Error al procesar notificación de usuario: {str(e)}")
        raise


"""
def process_course_notification(notification: CourseNotificationEvent):
    try:
        # Obtener todos los usuarios del curso

        # TODO: Implementar lógica para obtener usuarios del curso, comunicarse con el otro servicio
        # y para cada usuario que puedo obtener la info mando la notificacion con el process user? o armo otra fn?
        # user = obtenerlo pidiendolo al servicio de cursos segun el id de course

        # Procesar según el tipo de evento
        if should_notify(user, notification.notification_type, "email"):
            logging.info(
                f"Procesando notificación de entrega para usuario {notification.id_user}"
            )
            send_email(notification.email, subject, body)

        if should_notify(user, notification.notification_type, "push"):
            # TODO: Implementar lógica para notificación de calificación
            logging.info(
                f"Procesando notificación de calificación para usuario {notification.id_user}"
            )

    except Exception as e:
        logging.error(f"Error al procesar notificación de curso: {str(e)}")
        raise
"""


def should_notify(user, notification_type: str, method: str) -> bool:
    if notification_type == "Tarea":
        return getattr(user, f"tarea_{method}", False)
    elif notification_type == "Examen":
        return getattr(user, f"examen_{method}", False)
    return False
