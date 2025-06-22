from pydantic import BaseModel
from typing import Literal
from enum import Enum


class NotificationEventType(str, Enum):
    USER = "user_notification"
    COURSE = "course_notification"
    AUX_TEACHER = "aux_teacher_notification"


class NotificationEventData(BaseModel):
    titulo: str
    descripcion: str | None = None
    fecha: str
    instrucciones: str | None = None
    nota: float | None = None
    feedback: str | None = None
    hora: str | None = None


class UserNotificationEvent(BaseModel):
    event_type: NotificationEventType = NotificationEventType.USER
    id_user: int
    notification_type: Literal["Examen", "Tarea"]
    event: Literal["Entregado", "Calificado"]
    data: NotificationEventData

    class Config:
        json_schema_extra = {
            "example": {
                "id_user": 1,
                "email": "usuario@ejemplo.com",
                "notification_type": "Tarea",
                "event": "Nuevo",
                "data": {
                    "titulo": "Tarea 1",
                    "descripcion": "Descripción de la tarea",
                    "fecha": "2024-03-20",
                    "instrucciones": "Instrucciones de la tarea",
                },
            }
        }


class CourseNotificationEvent(BaseModel):
    event_type: NotificationEventType = NotificationEventType.COURSE
    id_course: str
    notification_type: Literal["Examen", "Tarea"]
    event: Literal["Nuevo", "Actualizado"]
    data: NotificationEventData

    class Config:
        json_schema_extra = {
            "example": {
                "id_course": "curso-123",
                "notification_type": "Tarea",
                "event": "Nuevo",
                "data": {
                    "titulo": "Tarea 1",
                    "descripcion": "Descripción de la tarea",
                    "fecha": "2024-03-20",
                    "instrucciones": "Instrucciones de la tarea",
                },
            }
        }


class UserPreferences(BaseModel):
    examen_email: bool | None = None
    examen_push: bool | None = None
    tarea_email: bool | None = None
    tarea_push: bool | None = None


class FCMToken(BaseModel):
    fcm_token: str


class UserPermissions(
    BaseModel
):  # TODO ojo con el update y como llega porque si pongo todo false y envio el mensaje con esa info va a estar mal
    edit_course: bool = False
    create_module: bool = False
    create_task: bool = False
    grade_task: bool = False


class AuxiliaryTeacherNotificationEvent(BaseModel):
    event_type: NotificationEventType = NotificationEventType.AUX_TEACHER
    event: Literal["add", "remove", "update"]
    id_course: str
    teacher_id: int
    permissions: UserPermissions = None  # en delete este campo no viene
