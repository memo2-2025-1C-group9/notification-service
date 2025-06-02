#!/usr/bin/env python

from fastapi import HTTPException, status
import pika
from app.core.config import settings
import logging
from typing import Any, Dict
import json


class QueueRepository:
    _connection = None
    _channel = None

    def __init__(self):
        self._connect()

    def _connect(self):
        try:
            params = pika.URLParameters(settings.RABBITMQ_HOST)
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
            logging.info("Conexión a RabbitMQ establecida correctamente")
        except Exception as e:
            logging.error(f"Error al conectar con RabbitMQ: {str(e)}")
            raise

    def send_message(self, message: Dict[str, Any]) -> bool:
        try:
            logging.info(f"Enviando mensaje a RabbitMQ: {message}")
            if not self._connection or self._connection.is_closed:
                logging.info("Conexión a RabbitMQ está cerrada, reconectando...")
                self._connect()

            message_json = json.dumps(message)
            self._channel.basic_publish(
                exchange="", routing_key=settings.RABBITMQ_QUEUE, body=message_json
            )

            logging.info(f"Mensaje enviado a la queue: {message_json}")
            return True

        except Exception as e:
            logging.error(f"Error al enviar mensaje a RabbitMQ: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor",
            )

    def close(self):
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            logging.info("Conexión a RabbitMQ cerrada")
