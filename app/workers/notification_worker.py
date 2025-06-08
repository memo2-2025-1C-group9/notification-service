import asyncio
import time
from app.services.notification_processor import process_message
from app.core.config import settings
from app.repositories.queue_repository import QueueRepository
import logging


def callback(ch, method, properties, body):
    loop = asyncio.new_event_loop()  # pika usa callbacks sincronos.
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
            time.sleep(3)

    logging.info("Conectado a RabbitMQ, escuchando mensajes en la queue")
    channel = queue_repo._channel

    channel.basic_consume(
        queue=settings.RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True
    )

    channel.start_consuming()
