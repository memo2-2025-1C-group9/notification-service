import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.schemas.notification_schemas import UserPreferences
from app.controller.user_controller import (
    handle_validate_user,
    handle_get_user,
    handle_edit_user,
)
import logging

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
)


@router.get("/me/preferences")
async def get_user_preferences(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    try:
        # Validar el user con el auth service
        user_id = await handle_validate_user(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        return handle_get_user(db, user_id)

    except HTTPException:
        raise

    except Exception as e:
        logging.error(
            f"Exception no manejada al obtener preferencias de usuario: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


# Actualizar preferencias del usuario, se valida con el token
#   Si no existe devuelvo error
@router.put("/me/editpreferences")
async def get_user_preferences(
    token: Annotated[str, Depends(oauth2_scheme)],
    preferences: UserPreferences,
    db: Session = Depends(get_db),
):
    try:
        # Validar el user con el auth service
        user_id = await handle_validate_user(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        return handle_edit_user(db, user_id, preferences)

    except HTTPException:
        raise

    except Exception as e:
        logging.error(
            f"Exception no manejada al editar preferencias de usuario: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )
