# app/domain/notification_formatter.py
from datetime import datetime
from typing import Tuple, Dict, Callable
from app.schemas.notification_schemas import (
    UserNotificationEvent,
    AuxiliaryTeacherNotificationEvent,
    CourseNotificationEvent,
)


def formatear_fecha_legible(fecha_str):
    if not fecha_str:
        return None

    try:
        fecha = datetime.fromisoformat(fecha_str)

        return fecha.strftime("%d/%m/%Y, %H:%M hs")
    except Exception as e:
        return None


def format_nuevo(notification: UserNotificationEvent | CourseNotificationEvent):
    fecha_formateada = formatear_fecha_legible(notification.data.fecha)

    mensaje = f"{notification.data.descripcion}\n{notification.data.instrucciones}"
    if fecha_formateada:
        mensaje += f"\nFecha: {fecha_formateada}"

    return (
        f"[{notification.notification_type}] {notification.data.titulo}",
        mensaje,
    )


def format_actualizado(notification: UserNotificationEvent | CourseNotificationEvent):
    fecha_formateada = formatear_fecha_legible(notification.data.fecha)

    mensaje = "Se actualizaron los datos.\n{notification.data.instrucciones}"
    if fecha_formateada:
        mensaje += f"\nFecha: {fecha_formateada}"

    return (
        f"[{notification.notification_type}] {notification.data.titulo} (Actualizado)",
        mensaje,
    )


def format_entregado(notification: UserNotificationEvent | CourseNotificationEvent):
    fecha_formateada = formatear_fecha_legible(notification.data.fecha)

    mensaje = f"Tu entrega fue recibida"
    if fecha_formateada:
        mensaje += f" el {fecha_formateada}"

    return (
        f"[{notification.notification_type}] Entrega recibida: {notification.data.titulo}",
        mensaje,
    )


def format_calificado(notification: UserNotificationEvent | CourseNotificationEvent):
    fecha_formateada = formatear_fecha_legible(notification.data.fecha)

    mensaje = (
        f"Nota: {notification.data.nota}\nComentarios: {notification.data.feedback}"
    )
    if fecha_formateada:
        mensaje += f"\nFecha: {fecha_formateada}"

    return (
        f"[{notification.notification_type}] {notification.data.titulo} calificado",
        mensaje,
    )


def format_add_aux_teacher(notificacion: AuxiliaryTeacherNotificationEvent):
    return (
        "Bienvenido como docente auxiliar",
        f"Has sido invitado como docente auxiliar al curso: {notificacion.course_name}.\n\nPermisos otorgados:\n"
        + (
            f"• Editar curso: {'Sí' if notificacion.permissions.edit_course else 'No'}\n"
            if notificacion.permissions
            else ""
        )
        + (
            f"• Crear módulos: {'Sí' if notificacion.permissions.create_module else 'No'}\n"
            if notificacion.permissions
            else ""
        )
        + (
            f"• Crear tareas: {'Sí' if notificacion.permissions.create_task else 'No'}\n"
            if notificacion.permissions
            else ""
        )
        + (
            f"• Calificar tareas: {'Sí' if notificacion.permissions.grade_task else 'No'}\n"
            if notificacion.permissions
            else ""
        ),
    )


def format_remove_aux_teacher(notificacion: AuxiliaryTeacherNotificationEvent):
    return (
        "Acceso removido como docente auxiliar",
        f"Tu acceso como docente auxiliar al curso: {notificacion.course_name} ha sido removido.",
    )


def format_update_aux_teacher(notificacion: AuxiliaryTeacherNotificationEvent):
    return (
        "Permisos actualizados como docente auxiliar",
        f"Tus permisos como docente auxiliar para el curso: {notificacion.course_name} han sido actualizados.\n\nNuevos permisos:\n"
        + (
            f"• Editar curso: {'Sí' if notificacion.permissions.edit_course else 'No'}\n"
            if notificacion.permissions
            else ""
        )
        + (
            f"• Crear módulos: {'Sí' if notificacion.permissions.create_module else 'No'}\n"
            if notificacion.permissions
            else ""
        )
        + (
            f"• Crear tareas: {'Sí' if notificacion.permissions.create_task else 'No'}\n"
            if notificacion.permissions
            else ""
        )
        + (
            f"• Calificar tareas: {'Sí' if notificacion.permissions.grade_task else 'No'}\n"
            if notificacion.permissions
            else ""
        ),
    )


def format_entrega_owner(notification: UserNotificationEvent):
    fecha_formateada = formatear_fecha_legible(notification.data.fecha)

    mensaje = f"El usuario {notification.id_user} ha realizado una entrega de [{notification.notification_type}]: {notification.data.titulo}."

    if fecha_formateada:
        mensaje += f"\nFecha: {fecha_formateada}"

    return (
        f"[{notification.notification_type}] {notification.data.titulo}",
        mensaje,
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
    "EntregaOwner": format_entrega_owner,
}


def format_notification(
    notification_type: str,
    event: str,
    notification: UserNotificationEvent
    | AuxiliaryTeacherNotificationEvent
    | CourseNotificationEvent,
) -> Tuple[str, str]:
    """
    Devuelve (titulo, mensaje) listos para ser enviados.
    """
    formatter = event_formatters.get(event)
    if not formatter:
        return ("Notificación", "Evento desconocido.")

    subject, body = formatter(notification)
    return (subject, body)
