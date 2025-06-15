import json
import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import settings
import logging


def initialize_firebase():
    """
    Inicializa la conexión con Firebase Admin SDK.
    Nota: Necesitarás colocar tu archivo de credenciales de Firebase en la carpeta config/
    """
    try:
        # Intenta obtener la aplicación existente
        firebase_admin.get_app()
    except ValueError:
        # Si no existe, inicializa una nueva
        cred = credentials.Certificate(
            json.loads(settings.FIREBASE_ADMIN_SDK_CREDENTIALS)
        )
        firebase_admin.initialize_app(cred)

        logging.info("Firebase Admin SDK inicializado correctamente.")


def send_push_notification(fcm_token: str, title: str, body: str):
    logging.info(
        f"Enviando notificación push a {fcm_token} con título '{title}' y cuerpo '{body}'"
    )
    try:
        initialize_firebase()
    except Exception as e:
        logging.info(f"Error al inicializar Firebase: {str(e)}")
    try:
        # Probablemente el body sea enorme para una push
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body), token=fcm_token
        )

        response = messaging.send(message)
        logging.info(f"Notificación enviada exitosamente: {response}")
        return True
    except Exception as e:
        logging.info(f"Error al enviar la notificación: {str(e)}")
        return False
