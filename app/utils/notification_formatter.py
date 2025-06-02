# app/domain/notification_formatter.py

from typing import Tuple, Dict, Callable
from app.schemas.notification_schemas import NotificationEventData

# TODO: Toda esta data y formatos de mensajes anotarlo en el README

# Desde el assessment recibo:
"""
Esto me llega para Examen/Tarea Nuevo/Actualizado
payload = {
    "id_course": task_result.course_id,
    "notification_type": "Tarea",
    "event": event,
    "data": {
        "titulo": task_result.title,
        "descripcion": task_result.description,
        "fecha": task_result.start_date.isoformat(),
        "instrucciones": task_result.instructions,
    },
}
"""


def format_nuevo(data: NotificationEventData):
    return (
        f"{data.titulo}",
        f"{data.descripcion}\nFecha: {data.fecha}\n{data.instrucciones}",
    )


def format_actualizado(data: NotificationEventData):
    return (
        f"{data.titulo} (Actualizado)",
        f"Se actualizaron los datos.\nFecha: {data.fecha}\n{data.instrucciones}",
    )


def format_entregado(data: NotificationEventData):
    return (
        f"Entrega recibida: {data.titulo}",
        f"Tu entrega fue recibida el {data.fecha} a las {data.hora}.",
    )


def format_calificado(data: NotificationEventData):
    return (
        f"{data.titulo} calificado",
        f"Nota: {data.nota}\nComentarios: {data.feedback}\nFecha: {data.fecha} a las {data.hora}",
    )


# Tabla de funciones por evento
event_formatters: Dict[str, Callable[[Dict], Tuple[str, str]]] = {
    "Nuevo": format_nuevo,
    "Actualizado": format_actualizado,
    "Entregado": format_entregado,
    "Calificado": format_calificado,
}


def format_notification(
    notification_type: str, event: str, data: NotificationEventData
) -> Tuple[str, str]:
    """
    Devuelve (titulo, mensaje) listos para ser enviados.
    """
    formatter = event_formatters.get(event)
    if not formatter:
        return ("Notificación", "Evento desconocido.")

    subject, body = formatter(data)
    return (f"[{notification_type}] {subject}", body)
