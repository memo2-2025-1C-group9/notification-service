from fastapi import HTTPException
from app.core.config import settings
from sqlalchemy.orm import Session
from app.schemas.notification_schemas import UserPreferences
from app.repositories.user_repository import get_user_by_id, create_user, update_user
from app.core.auth import get_service_auth
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
            raise HTTPException(
                status_code=response.status_code,
                detail="Token inválido o expirado",
            )

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


async def get_info_user(user_id: int, retry: bool = True):
    """
    Obtiene la información del usuario.
    """
    try:
        auth_service = get_service_auth()
        access_token = auth_service.get_token()

        logging.info(f"Obteniendo información del usuario con id: {user_id}...")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/user/{user_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 200:
                user_data = response.json()
                return user_data
            else:
                if response.status_code == 401 and retry:
                    logging.warning("Token expirado o inválido, intentando renovar...")
                    await auth_service.login()
                    return await get_info_user(user_id, retry=False)
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error al obtener informacion del usuario (ID {user_id})",
                )
    except HTTPException as e:
        raise e

    except httpx.RequestError as e:
        logging.error(f"Error al conectar con el servicio de usuarios: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al conectar con el servicio de usuarios"
        )
