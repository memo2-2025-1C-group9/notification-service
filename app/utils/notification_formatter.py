# app/domain/notification_formatter.py

from typing import Tuple, Dict, Callable
from app.schemas.notification_schemas import NotificationEventData, AuxiliaryTeacherNotificationEvent


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
        f"Tu entrega fue recibida el {data.fecha}.",
    )


def format_calificado(data: NotificationEventData):
    return (
        f"{data.titulo} calificado",
        f"Nota: {data.nota}\nComentarios: {data.feedback}\nFecha: {data.fecha}",
    )


def format_add_aux_teacher(notificacion: AuxiliaryTeacherNotificationEvent):
    return (
        "Bienvenido como docente auxiliar",
        f"Has sido invitado como docente auxiliar al curso.\n\nPermisos otorgados:\n" +
        (f"• Editar curso: {'Sí' if notificacion.permissions.edit_course else 'No'}\n" if notificacion.permissions else "") +
        (f"• Crear módulos: {'Sí' if notificacion.permissions.create_module else 'No'}\n" if notificacion.permissions else "") +
        (f"• Crear tareas: {'Sí' if notificacion.permissions.create_task else 'No'}\n" if notificacion.permissions else "") +
        (f"• Calificar tareas: {'Sí' if notificacion.permissions.grade_task else 'No'}\n" if notificacion.permissions else "")
    )


def format_remove_aux_teacher(notificacion: AuxiliaryTeacherNotificationEvent):
    return (
        "Acceso removido como docente auxiliar",
        f"Tu acceso como docente auxiliar al curso: {notificacion.id_course} ha sido removido."
    )


def format_update_aux_teacher(notificacion: AuxiliaryTeacherNotificationEvent):
    return (
        "Permisos actualizados como docente auxiliar",
        f"Tus permisos como docente auxiliar han sido actualizados.\n\nNuevos permisos:\n" +
        (f"• Editar curso: {'Sí' if notificacion.permissions.edit_course else 'No'}\n" if notificacion.permissions else "") +
        (f"• Crear módulos: {'Sí' if notificacion.permissions.create_module else 'No'}\n" if notificacion.permissions else "") +
        (f"• Crear tareas: {'Sí' if notificacion.permissions.create_task else 'No'}\n" if notificacion.permissions else "") +
        (f"• Calificar tareas: {'Sí' if notificacion.permissions.grade_task else 'No'}\n" if notificacion.permissions else "")
    )


# Tabla de funciones por evento
event_formatters: Dict[str, Callable[[Dict], Tuple[str, str]]] = {
    "Nuevo": format_nuevo,
    "Actualizado": format_actualizado,
    "Entregado": format_entregado,
    "Calificado": format_calificado,
    "add": format_add_aux_teacher,
    "remove": format_remove_aux_teacher,
    "update": format_update_aux_teacher,
}


def format_notification(
    notification_type: str, event: str, data: NotificationEventData | AuxiliaryTeacherNotificationEvent
) -> Tuple[str, str]:
    """
    Devuelve (titulo, mensaje) listos para ser enviados.
    """
    formatter = event_formatters.get(event)
    if not formatter:
        return ("Notificación", "Evento desconocido.")

    subject, body = formatter(data)
    return (f"[{notification_type}] {subject}", body)
