from fastapi import HTTPException
from app.schemas.notification_schemas import (
    UserNotificationEvent,
    CourseNotificationEvent,
    AuxiliaryTeacherNotificationEvent,
    NotificationEventType
)
from app.schemas.user_schema import UserInfo
from app.repositories.user_repository import get_user_by_id, create_user
from app.services.courses_service import get_course_users
from app.services.email_notification import send_email
from app.services.user_service import get_info_user
from app.utils.notification_formatter import format_notification
from app.db.session import SessionLocal
from app.repositories.notification_log_repository import create_log
from app.services.push_notification_service import send_push_notification
import json
import logging


def get_user_preferences(user_id: int):
    db = None
    try:
        db = SessionLocal()

        user = get_user_by_id(db, user_id)
        if not user:  # Usuario no registrado, crearlo con valores default
            logging.info(f"Usuario no registrado, creando usuario con ID: {user_id}")
            user = create_user(db, user_id)
        return user
    except Exception as e:
        logging.error(f"Error al obtener usuario: {str(e)}")
        raise


async def process_message(body: bytes):
    try:
        # Decodificar el mensaje de bytes a string
        message_str = body.decode("utf-8")
        message_dict = json.loads(message_str)
        logging.info(f"Mensaje recibido: {message_dict}")
        # Determinar el tipo de mensaje basado en las claves presentes
        event_type = message_dict.get("event_type")
        if event_type == NotificationEventType.USER:
            notification = UserNotificationEvent(**message_dict)
            await process_user_notification(notification)
        elif event_type == NotificationEventType.COURSE:
            notification = CourseNotificationEvent(**message_dict)
            await process_course_notification(notification)
        elif event_type == NotificationEventType.AUX_TEACHER:
            notification = AuxiliaryTeacherNotificationEvent(**message_dict)
            await process_aux_teacher_notification(notification)
        else:  # No deberia entrar nunca aca, se valida el formato con el endpoint de la API
            logging.error(f"Mensaje con formato inválido: {message_dict}")

    except json.JSONDecodeError as e:
        logging.error(f"Error al decodificar el mensaje JSON: {str(e)}")
    except Exception as e:
        logging.error(f"Error al procesar el mensaje: {str(e)}")


def should_notify(user, notification_type: str, method: str) -> bool:
    if notification_type == "Tarea":
        return getattr(user, f"tarea_{method}", False)
    elif notification_type == "Examen":
        return getattr(user, f"examen_{method}", False)
    return False


def send_notifications(user, user_id, email, notification, subject, body):
    if notification.event_type == NotificationEventType.AUX_TEACHER or should_notify(user, notification.notification_type, "email"):
        logging.info(
            f"Procesando notificación EMAIL para usuario {user_id}"
        )
        try:
            send_email(email, subject, body)

            create_log(
                db=SessionLocal(),
                user_id=user_id,
                notification_type=notification.notification_type if notification.event_type != NotificationEventType.AUX_TEACHER else "Auxiliar",
                event=notification.event,
                method="email",
                subject=subject,
                body=body,
            )
        except Exception as e:
            logging.error(
                f"Error al enviar notificación EMAIL para usuario {user_id}: {str(e)}"
            )

    if notification.event_type == NotificationEventType.AUX_TEACHER or should_notify(user, notification.notification_type, "push"):
        logging.info(
            f"Procesando notificación de PUSH para usuario {user_id}"
        )
        try:
            send_push_notification(user.token_fcm, subject, body)

            create_log(
                db=SessionLocal(),
                user_id=user_id,
                notification_type=notification.notification_type if notification.event_type != NotificationEventType.AUX_TEACHER else "Auxiliar",
                event=notification.event,
                method="push",
                subject=subject,
                body=body,
            )
        except Exception as e:
            logging.error(
                f"Error al enviar notificación PUSH para usuario {user_id}: {str(e)}"
            )


async def process_user_notification(notification: UserNotificationEvent):
    try:
        logging.info(
            f"Procesando notificación de usuario: {notification.id_user}, tipo: {notification.notification_type}, evento: {notification.event}"
        )

        user_id = notification.id_user

        # Obtener las preferencias del usuario
        user = get_user_preferences(user_id)

        # Buscar usuario por id para el email, no lo recibo desde assessments
        try:
            user_data_info = await get_info_user(user_id)
            user_info = UserInfo(**user_data_info)
        except Exception:
            logging.error(f"Error al obtener información del usuario {user_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener información del usuario: {user_id}",
            )
        logging.info(f"Usuario obtenido: {user_info}")
        subject, body = format_notification(
            notification.notification_type, notification.event, notification.data
        )

        send_notifications(user, user_id, user_info.email, notification, subject, body)

    except Exception as e:
        logging.error(f"Error al procesar notificación de usuario: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar notificación de usuario"
        )


async def process_course_notification(notification: CourseNotificationEvent):
    try:
        logging.info(
            f"Procesando notificación de curso: {notification.id_course}, tipo: {notification.notification_type}, evento: {notification.event}"
        )

        # Obtener todos los usuarios del curso
        user_list = await get_course_users(notification.id_course)
        if not user_list:
            logging.warning(
                f"No se encontraron usuarios para el curso {notification.id_course}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener informacion del curso: {notification.id_course}",
            )

        for user_id in user_list:
            try:
                user_data_info = await get_info_user(user_id)
                user_info = UserInfo(**user_data_info)
            except Exception:
                logging.error(f"Error al obtener información del usuario {user_id}")
                continue
            logging.info(f"Usuario obtenido: {user_info}")

            # Obtener las preferencias del usuario
            user = get_user_preferences(user_id)

            subject, body = format_notification(
                notification.notification_type, notification.event, notification.data
            )

            send_notifications(
                user, user_id, user_info.email, notification, subject, body
            )

    except HTTPException:
        raise

    except Exception as e:
        logging.error(f"Error al procesar notificación de curso: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar notificación de curso"
        )
    

async def process_aux_teacher_notification(notification: AuxiliaryTeacherNotificationEvent):
    try:
        logging.info(
            f"Procesando notificación de docente auxiliar: {notification.id_course}, tipo: {notification.event_type}, evento: {notification.event}"
        )

        user_id = notification.teacher_id

        # Obtener las preferencias del usuario
        user = get_user_preferences(user_id)

        # Buscar usuario por id para el email, no lo recibo desde courses
        try:
            user_data_info = await get_info_user(user_id)
            user_info = UserInfo(**user_data_info)
        except Exception:
            logging.error(f"Error al obtener información del usuario {user_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener información del usuario: {user_id}",
            )

        logging.info(f"notification: {notification}")

        subject, body = format_notification(
            notification.event_type, notification.event, notification
        )

        send_notifications(user, user_id, user_info.email, notification, subject, body)


    except HTTPException:
        raise

    except Exception as e:
        logging.error(f"Error al procesar notificación de docente auxiliar: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al procesar notificación de docente auxiliar"
        )