# La idea es la siguiente:
# 1. El worker va a estar escuchando en la queue
# 2. Va a recibir el mensaje
#       y tengo que tener la manera de saber:
#            Que tipo de mensaje es
#            El email y tokenFMC del usuario (El token lo voy a tener en la base de datos)
#            Y las preferencias del usuario en cuanto a que tipo de notificaciones quiere recibir segun el evento

# Estructura de mensaje
# {
#     "id_user": int,
#     "email": email,
#     "notification_type": "Examen" | "Tarea",
#     "event": "Nuevo" | "Actualizado" | "Entregado" | "Calificado",
#     "data": { Aca depende del evento }
# }

# Data segun evento
#  "Nuevo" : { titulo, descripcion, fecha, instrucciones?}
#  "Actualizado" : lo mismo que nuevo pero con los cambios
#  "Entregado" : {titulo, fecha, hora} Avisa que se recibio la entrega # Esto es relevante?
#  "Calificado" : {titulo, nota, feedback, fecha, hora} Avisa que se califico la entrega

import time
import pika
from app.services.notification_processor import process_message
from app.core.config import settings
import logging


def callback(ch, method, properties, body):
    try:
        process_message(body)
    except Exception as e:
        logging.error(f"Error al procesar el mensaje: {str(e)}")


def worker_main():
    for i in range(10):
        try:
            logging.info(f"Intentando conectar a RabbitMQ {1+i}/10")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
            )
            logging.info(f"Conexion a RabbitMQ exitosa")
            break
        except Exception:
            logging.error(f"Error al conectar a RabbitMQ {1+i}/10")
            if i == 9:
                raise
            time.sleep(
                2
            )  # En el docker compose tarda un poco en levantar el servicio de RabbitMQ

    channel = connection.channel()

    channel.queue_declare(queue=settings.RABBITMQ_QUEUE)

    channel.basic_consume(
        queue=settings.RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True
    )

    logging.info(f"Waiting for messages. Queue: {settings.RABBITMQ_QUEUE}")
    channel.start_consuming()
