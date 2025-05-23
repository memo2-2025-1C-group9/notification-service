# La idea es la siguiente:
# 1. El worker va a estar escuchando en la queue
# 2. Va a recibir el mensaje
#       y tengo que tener la manera de saber:
#            Que tipo de mensaje es
#            El email y tokenFMC del usuario (El token lo voy a tener en la base de datos)
#            Y las preferencias del usuario en cuanto a que tipo de notificaciones quiere recibir segun el evento

from app.schemas.notification_schemas import NotificationMessage
from app.repositories.user_repository import get_user_by_id, create_user
from app.services.email_notification import send_email
from app.utils.notification_formatter import format_notification
from app.db.session import SessionLocal
import json
import logging


def process_message(bytes_message):
    """
    Process the incoming message from RabbitMQ.
    """
    db = None
    try:
        db = SessionLocal()
        # Parsear el mensaje, llega de la queue como bytes
        json_str = bytes_message.decode("utf-8")
        data_dict = json.loads(json_str)
        message = NotificationMessage(**data_dict)

        logging.info(f"Procesando mensaje: {message}")

        user_id = message.id_user

        user = get_user_by_id(db, user_id)
        if not user:  # Usuario no registrado, crearlo con valores default
            logging.info(f"Usuario no registrado, creando usuario con ID: {user_id}")
            user = create_user(db, user_id)

        # Existe el user, enviar notificaciones

        # Armar el mensaje segun el tipo de notificacion
        subject, body = format_notification(  # TODO: Funcion a chequear
            message.notification_type, message.event, message.data
        )

        # TODO: Despues sacar estos if's horribles
        if message.notification_type == "Examen":
            logging.info(f"Enviando notificacion de examen a {message.email}")
            if user.examen_email:
                # Enviar notificacion de examen por email
                send_email(message.email, subject, body)

            if user.examen_push:
                # Enviar notificacion de examen por push
                pass

        if message.notification_type == "Tarea":
            logging.info(f"Enviando notificacion de tarea a {message.email}")
            if user.tarea_email:
                # Enviar notificacion de tarea por email
                send_email(message.email, subject, body)

            if user.tarea_push:
                # Enviar notificacion de tarea por push
                pass

    except Exception as e:
        logging.error(f"Error al procesar el mensaje: {str(e)}")
        raise
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logging.error(f"Error al cerrar conexión DB: {str(e)}")
