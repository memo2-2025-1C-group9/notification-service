from contextlib import asynccontextmanager
import threading
from fastapi import FastAPI, HTTPException, Request
from app.utils.problem_details import problem_detail_response
from app.core.auth import get_service_auth
from app.db.base import Base
from app.db.session import engine
import logging
import traceback
from app.workers.notification_worker import worker_main
from app.routers.notification_router import router as notification_router
from app.core.config import settings

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


app = FastAPI(lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Determinar el título basado en el código de status
    title = "Error de Servidor"
    if exc.status_code == 401:
        title = "No Autorizado"
    elif exc.status_code == 403:
        title = "Prohibido"
    elif exc.status_code == 404:
        title = "No Encontrado"
    elif exc.status_code == 400:
        title = "Solicitud Incorrecta"
    elif exc.status_code == 422:
        title = "Error de Validación"
    elif exc.status_code < 500:
        title = "Error de Cliente"

    logging.error(
        f"HTTPException manejada: {exc.detail} (status: {exc.status_code}, url: {request.url})"
    )

    headers = exc.headers or {}

    headers["Content-Type"] = "application/problem+json"

    headers["Access-Control-Allow-Origin"] = "*"

    return problem_detail_response(
        status_code=exc.status_code,
        title=title,
        detail=exc.detail,
        instance=str(request.url),
        headers=headers,
    )


app.include_router(notification_router)


@app.get("/health")
def get_health():
    return {"status": "ok"}
