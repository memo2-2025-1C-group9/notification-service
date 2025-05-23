from fastapi import HTTPException
from app.core.config import settings
from sqlalchemy.orm import Session
from app.schemas.notification_schemas import UserPreferences
from app.repositories.user_repository import get_user_by_id, create_user, update_user
import httpx
import logging


async def validate_user(token: str):
    """
    Valida al usuario con el auth service y devuelve el id del usuario.
    """
    # Llamar al auth service para validar el token
    async with httpx.AsyncClient() as client:
        try:
            logging.info(f"Validando identidad del usuario con el token: {token}...")

            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/me/",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code == 200:
                logging.info("Token valido")
                user_data = response.json()
                user_id = user_data.get("id")
                return user_id
            return None

        except httpx.RequestError as e:
            logging.error(f"Error al conectar con el servicio de usuarios: {str(e)}")
            logging.error(f"URL: {settings.AUTH_SERVICE_URL}/me/")
            raise HTTPException(
                status_code=500,
                detail="Error al conectar con el servicio de usuarios",
            )


def get_user(db: Session, user_id: int):
    try:
        logging.info(f"Obteniendo usuario con id: {user_id}...")
        user = get_user_by_id(db, user_id)
        if (
            not user
        ):  # Decision de diseño: si no existe el usuario en la base de datos, lo creo
            logging.info(
                f"Usuario no encontrado en la base de datos, creando nuevo usuario..."
            )
            user = create_user(db, user_id)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener usuario: {str(e)}"
        )


def edit_user(db: Session, user_id: int, preferences: UserPreferences):
    try:
        return update_user(db, user_id, preferences)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al editar preferencias de usuario: {str(e)}"
        )
