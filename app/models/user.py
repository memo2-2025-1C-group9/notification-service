from sqlalchemy import Column, Integer, Boolean, String
from app.db.base import Base


class User(Base):
    __tablename__ = "user-preferences"
    id = Column(Integer, primary_key=True, index=True)
    tarea_email = Column(Boolean, default=True, nullable=False)
    tarea_push = Column(Boolean, default=True, nullable=False)

    examen_email = Column(Boolean, default=True, nullable=False)
    examen_push = Column(Boolean, default=True, nullable=False)

    token_fcm = Column(String, nullable=True)
