from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    notification_type = Column(String, nullable=False)  # Tarea o Examen
    event = Column(String, nullable=False)  # Nuevo, Actualizado, Entregado, Calificado
    method = Column(String, nullable=False)  # email o push
    subject = Column(String, nullable=False)  # Asunto del email
    body = Column(String, nullable=False)  # Cuerpo del email o mensaje push

    created_at = Column(DateTime(timezone=True), server_default=func.now())
