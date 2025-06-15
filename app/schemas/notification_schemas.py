from pydantic import BaseModel
from typing import Literal


class NotificationEventData(BaseModel):
    titulo: str
    descripcion: str | None = None
    fecha: str
    instrucciones: str | None = None
    nota: float | None = None
    feedback: str | None = None
    hora: str | None = None


class UserNotificationEvent(BaseModel):
    id_user: int
    # email: EmailStr no se recibe el email
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