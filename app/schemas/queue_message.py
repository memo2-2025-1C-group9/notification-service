# Estructura de mensaje
# {
#     "id_user": int,
#     "email": email,
#     "notification_type": "Examen" | "Tarea",
#     "event": "Nuevo" | "Actualizado" | "Entregado" | "Calificado",
#     "data": { Aca depende del evento }
# }

from pydantic import BaseModel, EmailStr
from typing import Literal, Dict, Any


class NotificationMessage(BaseModel):
    id_user: int
    email: EmailStr
    notification_type: Literal["Examen", "Tarea"]
    event: Literal["Nuevo", "Actualizado", "Entregado", "Calificado"]
    data: Dict[str, Any]
