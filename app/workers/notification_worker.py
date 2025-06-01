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

import asyncio
import functools
import time
from app.services.notification_processor import process_message
from app.core.config import settings
from app.repositories.queue_repository import QueueRepository
import logging



def callback(ch, method, properties, body):
    loop = asyncio.new_event_loop() # pika usa callbacks sincronos.
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_message(body))
    finally:
        loop.close()


def worker_main():
    logging.info("Iniciando worker para procesar notificaciones")
    for i in range(10):
        try:
            logging.info(f"Intentando conectar a RabbitMQ {1+i}/10")
            queue_repo = QueueRepository()
            logging.info(f"Conexion a RabbitMQ exitosa")
            break
        except Exception:
            logging.error(f"Error al conectar a RabbitMQ {1+i}/10")
            if i == 9:
                raise
            time.sleep(
                3
            )  # En el docker compose tarda un poco en levantar el servicio de RabbitMQ

    logging.info("Conectado a RabbitMQ, escuchando mensajes en la queue")
    channel = queue_repo._channel

    channel.basic_consume(
        queue=settings.RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True
    )

    channel.start_consuming()
