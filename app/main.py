from contextlib import asynccontextmanager
import threading
from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
import logging
import traceback
from app.workers.notification_worker import worker_main

app = FastAPI()

logging.getLogger("pika").setLevel(logging.INFO)

# Crear todas las tablas al iniciar la aplicación
try:
    Base.metadata.create_all(bind=engine)
    logging.info("Tablas creadas correctamente en la base de datos")
except Exception as e:
    logging.error(f"Error al crear tablas en la base de datos: {str(e)}")
    logging.error(traceback.format_exc())

try:
    thread = threading.Thread(target=worker_main, daemon=True)
    thread.start()
    logging.info("Worker thread started")
except Exception as e:
    logging.error(f"Error starting worker thread: {str(e)}")
    logging.error(traceback.format_exc())


@app.get("/health")
def get_health():
    return {"status": "ok"}
