from contextlib import asynccontextmanager
import threading
from fastapi import FastAPI
from app.core.auth import get_service_auth
from app.db.base import Base
from app.db.session import engine
import logging
import traceback
from app.workers.notification_worker import worker_main
from app.routers.notification_router import router as notification_router
from app.core.config import settings
app = FastAPI()

logging.getLogger("pika").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa los servicios necesarios al arrancar la aplicación"""
    service_auth = get_service_auth()
    await service_auth.initialize()
    logging.info("Servicio de autenticación inicializado")
    yield

# TODO: Errores con RFC

app.include_router(notification_router)


@app.get("/health")
def get_health():
    return {"status": "ok"}
