# La idea es la siguiente:
# 1. El worker va a estar escuchando en la queue
# 2. Va a recibir el mensaje
#       y tengo que tener la manera de saber:
#            Que tipo de mensaje es
#            El email y tokenFMC del usuario (El token lo voy a tener en la base de datos)
#            Y las preferencias del usuario en cuanto a que tipo de notificaciones quiere recibir segun el evento

from app.schemas.queue_message import NotificationMessage
from app.repositories.user_repository import get_user_by_id, create_user
from app.services.email_notification import send_email


def process_message(message: NotificationMessage):
    """
    Process the incoming message from RabbitMQ.
    """
    # Parsear el mensaje, llega como bytes

    user_id = message.id_user

    user = get_user_by_id(user_id)
    if not user:  # Usuario no registrado, crearlo con valores default
        create_user(user_id)

    # Existe el user, enviar notificaciones

    # Armar el mensaje segun el tipo de notificacion
    subject, body = "Titulo de ejemplo para envio de notificaciones", {
        "datos": 1
    }  # funcion que arma el mensaje

    # TODO: Despues sacar estos if's horribles
    if user.tarea_email:
        send_email(user.email, subject, body)
        # Enviar notificacion de tarea por email
        pass
    if user.tarea_push:
        # Enviar notificacion de tarea por push
        pass
    if user.examen_email:
        send_email(user.email, subject, body)
        # Enviar notificacion de examen por email
        pass
    if user.examen_push:
        # Enviar notificacion de examen por push
        pass
