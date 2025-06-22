import traceback
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.schemas.notification_schemas import (
    UserPreferences,
    UserNotificationEvent,
    CourseNotificationEvent,
    FCMToken,
    AuxiliaryTeacherNotificationEvent,
)
from app.controller.user_controller import (
    handle_validate_user,
    handle_get_user,
    handle_edit_user,
    handle_get_user_logs,
    handle_edit_fcm_token,
)
from app.controller.notification_controller import handle_add_queue_message
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


@router.post("/notify/user")
async def create_user_notification(
    notification: UserNotificationEvent,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Crea una notificación de usuario y la agrega a la cola de mensajes.
    """
    try:
        try:
            await handle_validate_user(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        if handle_add_queue_message(notification):
            return {
                "success": True,
                "message": "Mensaje agregado a la cola correctamente.",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al agregar mensaje a la cola",
            )

    except HTTPException:
        raise

    except Exception as e:
        logging.error(
            f"Exception no manejada al crear notificación de usuario: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.post("/notify/course")
async def create_course_notification(
    notification: CourseNotificationEvent,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Crea una notificación de curso y la agrega a la cola de mensajes.
    """
    try:
        try:
            await handle_validate_user(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        if handle_add_queue_message(notification):
            return {
                "success": True,
                "message": "Mensaje agregado a la cola correctamente.",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al agregar mensaje a la cola",
            )

    except HTTPException:
        raise

    except Exception as e:
        logging.error(f"Exception no manejada al crear notificación de curso: {str(e)}")
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get("/me/logs")
async def get_my_notification_logs(
    token: Annotated[str, Depends(oauth2_scheme)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
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

        logs = handle_get_user_logs(db, user_id, skip, limit)
        return logs

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error al obtener logs de usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.put("/me/editfcmtoken")
async def edit_fmc_token(
    jwt_token: Annotated[str, Depends(oauth2_scheme)],
    user_fcm_token: FCMToken,
    db: Session = Depends(get_db),
):
    try:
        # Validar el user con el auth service
        user_id = await handle_validate_user(jwt_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        return handle_edit_fcm_token(db, user_id, user_fcm_token)

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


@router.post("/notify/auxiliary-teacher")
async def create_user_notification(
    notification: AuxiliaryTeacherNotificationEvent,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    """
    Crea una notificación de docente auxiliar y la agrega a la cola de mensajes.
    """
    try:
        try:
            await handle_validate_user(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
            )

        if handle_add_queue_message(notification):
            return {
                "success": True,
                "message": "Mensaje agregado a la cola correctamente.",
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al agregar mensaje a la cola",
            )

    except HTTPException:
        raise

    except Exception as e:
        logging.error(
            f"Exception no manejada al crear notificación de docente auxiliar: {str(e)}"
        )
        logging.error(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )
