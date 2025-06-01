# La idea es la siguiente:
# 1. El worker va a estar escuchando en la queue
# 2. Va a recibir el mensaje
#       y tengo que tener la manera de saber:
#            Que tipo de mensaje es
#            El email y tokenFMC del usuario (El token lo voy a tener en la base de datos)
#            Y las preferencias del usuario en cuanto a que tipo de notificaciones quiere recibir segun el evento

from fastapi import HTTPException
from app.schemas.notification_schemas import (
    UserNotificationEvent,
    CourseNotificationEvent,
)
from app.schemas.user_schema import UserInfo
from app.repositories.user_repository import get_user_by_id, create_user
from app.services.courses_service import get_course_users
from app.services.email_notification import send_email
from app.services.user_service import get_info_user
from app.utils.notification_formatter import format_notification
from app.db.session import SessionLocal
import json
import logging


async def process_message(body: bytes):
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
            await process_course_notification(notification)
        else:  # No deberia entrar nunca aca, se valida el formato con el endpoint de la API
            logging.error(f"Mensaje con formato inválido: {message_dict}")

    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar el mensaje JSON: {str(e)}")
    except Exception as e:
        logging.error(f"Error al procesar el mensaje: {str(e)}")


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

        # subject, body = format_notification(  # TODO: Funcion a chequear, tengo que armar el mensaje segun lo que me llega, cada tipo deberia traer info distinta
        #    notification.notification_type, notification.event, notification.data
        # )
        # Procesar según el tipo de evento
        if should_notify(user, notification.notification_type, "email"):
            logging.info(
                f"Procesando notificación de {notification.notification_type} EMAIL para usuario {notification.id_user}"
            )
            subject = f"{notification.notification_type} - {notification.event}"  # TODO: Esto es provisional, armar el mensaje con la funcion de format_notification
            body = f"{notification.notification_type} - {notification.event}\n{notification.data}"  # TODO: Esto es provisional, armar el mensaje con la funcion de format_notification
            send_email(notification.email, subject, body)

        if should_notify(user, notification.notification_type, "push"):
            # TODO: Implementar lógica para notificación push
            logging.info(
                f"Procesando notificación de {notification.notification_type} PUSH para usuario {notification.id_user}"
            )

    except Exception as e:
        logging.error(f"Error al procesar notificación de usuario: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar notificación de usuario"
        )



async def process_course_notification(notification: CourseNotificationEvent):
    db = None
    try:
        # Obtener todos los usuarios del curso
        logging.info(
            f"Procesando notificación de curso: {notification.id_course}, tipo: {notification.notification_type}, evento: {notification.event}"
        )

        db = SessionLocal()

        user_list = await get_course_users(notification.id_course)

        for user_id in user_list:
            try:
                user_data_info = await get_info_user(user_id)
                user_info = UserInfo(**user_data_info)
            except Exception:
                logging.error(f"Error al obtener información del usuario {user_id}")
                continue
            logging.info(f"Usuario obtenido: {user_info}")

            # Obtener las preferencias del usuario
            user = get_user_by_id(db, user_id)
            if not user:  # Usuario no registrado, crearlo con valores default
                logging.info(f"Usuario no registrado, creando usuario con ID: {user_id}")
                user = create_user(db, user_id)

            # Procesar según el tipo de evento
            if should_notify(user, notification.notification_type, "email"):
                logging.info(
                    f"Procesando notificación de entrega para usuario {user_id}"
                )
                subject = f"{notification.notification_type} - {notification.event}"  # TODO: Esto es provisional, armar el mensaje con la funcion de format_notification
                body = f"{notification.notification_type} - {notification.event}\n{notification.data}"  # TODO: Esto es provisional, armar el mensaje con la funcion de format_notification
                send_email(user_info.email, subject, body)

            if should_notify(user, notification.notification_type, "push"):
                # TODO: Implementar lógica para notificación de calificación
                logging.info(
                    f"Procesando notificación de calificación para usuario {user_id}"
                )
    except HTTPException:
        raise

    except Exception as e:
        logging.error(f"Error al procesar notificación de curso: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar notificación de curso"
        )



def should_notify(user, notification_type: str, method: str) -> bool:
    if notification_type == "Tarea":
        return getattr(user, f"tarea_{method}", False)
    elif notification_type == "Examen":
        return getattr(user, f"examen_{method}", False)
    return False
