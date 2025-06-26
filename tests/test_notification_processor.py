import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.services.notification_processor import (
    process_message,
    process_user_notification,
    process_course_notification,
    process_aux_teacher_notification,
    send_notifications,
    should_notify,
    get_user_preferences,
)
from app.schemas.notification_schemas import (
    UserNotificationEvent,
    CourseNotificationEvent,
    AuxiliaryTeacherNotificationEvent,
)
from app.models.user import User


# Datos de prueba para notificaciones de usuario
user_notification_data = {
    "event_type": "user_notification",
    "id_user": 1,
    "notification_type": "Tarea",
    "event": "Entregado",
    "data": {
        "titulo": "Tarea 1",
        "descripcion": "Descripción de la tarea",
        "fecha": "2024-03-20",
        "instrucciones": "Instrucciones de la tarea",
        "nota": 9.5,
        "feedback": "Excelente trabajo",
    },
}

# Datos de prueba para notificaciones de curso
course_notification_data = {
    "event_type": "course_notification",
    "id_course": "curso-123",
    "notification_type": "Tarea",
    "event": "Nuevo",
    "data": {
        "titulo": "Tarea 1",
        "descripcion": "Descripción de la tarea",
        "fecha": "2024-03-20",
    },
}

# Datos de prueba para notificaciones de docente auxiliar
auxiliary_teacher_data = {
    "event_type": "aux_teacher_notification",
    "event": "add",
    "id_course": "curso-123",
    "course_name": "Curso de Programación",
    "teacher_id": 1,
    "permissions": {
        "edit_course": True,
        "create_module": False,
        "create_task": True,
        "grade_task": False,
    },
}

# Datos de usuario de prueba
user_info_data = {
    "id": 1,
    "email": "usuario@test.com",
    "name": "Usuario Test",
}


@pytest.fixture
def mock_user_repository(self):
    with patch("app.services.notification_processor.get_user_by_id") as mock_get, \
         patch("app.services.notification_processor.create_user") as mock_create:
        yield {"get": mock_get, "create": mock_create}


@pytest.fixture
def mock_user_service(self):
    with patch("app.services.notification_processor.get_info_user") as mock:
        yield mock


@pytest.fixture
def mock_courses_service(self):
    with patch("app.services.notification_processor.get_course_users") as mock:
        yield mock


@pytest.fixture
def mock_email_service(self):
    with patch("app.services.notification_processor.send_email") as mock:
        yield mock


@pytest.fixture
def mock_push_service(self):
    with patch("app.services.notification_processor.send_push_notification") as mock:
        yield mock


@pytest.fixture
def mock_log_repository(self):
    with patch("app.services.notification_processor.create_log") as mock:
        yield mock


@pytest.fixture
def mock_format_notification(self):
    with patch("app.services.notification_processor.format_notification") as mock:
        mock.return_value = ("Asunto de prueba", "Cuerpo de prueba")
        yield mock


@pytest.fixture
def mock_session_local(self):
    with patch("app.services.notification_processor.SessionLocal") as mock:
        mock_session = MagicMock()
        mock.return_value = mock_session
        yield mock_session


def test_should_notify_tarea_email_enabled(self):
    """Test que verifica que should_notify devuelve True para tarea email habilitado"""
    user = User(tarea_email=True)
    result = should_notify(user, "Tarea", "email")
    assert result is True


def test_should_notify_tarea_email_disabled(self):
    """Test que verifica que should_notify devuelve False para tarea email deshabilitado"""
    user = User(tarea_email=False)
    result = should_notify(user, "Tarea", "email")
    assert result is False

def test_should_notify_tarea_push_enabled(self):
    """Test que verifica que should_notify devuelve True para tarea push habilitado"""
    user = User(tarea_push=True)
    result = should_notify(user, "Tarea", "push")
    assert result is True


def test_should_notify_tarea_push_disabled(self):
    """Test que verifica que should_notify devuelve False para tarea push deshabilitado"""
    user = User(tarea_push=False)
    result = should_notify(user, "Tarea", "push")
    assert result is False

def test_should_notify_examen_email_enabled(self):
    """Test que verifica que should_notify devuelve True para examen email habilitado"""
    user = User(examen_email=True)
    result = should_notify(user, "Examen", "email")
    assert result is True


def test_should_notify_examen_email_disabled(self):
    """Test que verifica que should_notify devuelve False para examen email deshabilitado"""
    user = User(examen_email=False)
    result = should_notify(user, "Examen", "email")
    assert result is False

def test_should_notify_examen_push_enabled(self):
    """Test que verifica que should_notify devuelve True para examen push habilitado"""
    user = User(examen_push=True)
    result = should_notify(user, "Examen", "push")
    assert result is True


def test_should_notify_examen_push_disabled(self):
    """Test que verifica que should_notify devuelve False para examen push deshabilitado"""
    user = User(examen_push=False)
    result = should_notify(user, "Examen", "push")
    assert result is False


def test_get_user_preferences_existing_user(self, mock_user_repository):
    """Test que verifica que get_user_preferences devuelve un usuario existente"""
    user = User(id=1, tarea_email=True, tarea_push=False)
    mock_user_repository["get"].return_value = user
    result = get_user_preferences(1)
    assert result == user


def test_get_user_preferences_create_new_user(self, mock_user_repository):
    """Test que verifica que get_user_preferences crea un nuevo usuario si no existe"""
    new_user = User(id=1)
    mock_user_repository["get"].return_value = None
    mock_user_repository["create"].return_value = new_user
    result = get_user_preferences(1)
    assert result == new_user


@pytest.mark.asyncio
async def test_send_notifications_aux_teacher_always_sends(self, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica que las notificaciones de docente auxiliar siempre se envían"""
    user = User(id=1, token_fcm="fcm_token_123")
    notification = AuxiliaryTeacherNotificationEvent(**auxiliary_teacher_data)
    
    await send_notifications(user, 1, "test@test.com", notification, "Asunto", "Cuerpo")
    
    # Verificar que se envio email
    mock_email_service.assert_called_once_with("test@test.com", "Asunto", "Cuerpo")
    # Verificar que se envio push
    mock_push_service.assert_called_once_with("fcm_token_123", "Asunto", "Cuerpo")
    # Verificar que se crearon logs
    assert mock_log_repository.call_count == 2


@pytest.mark.asyncio
async def test_send_notifications_user_email_enabled(self, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica que se envía email cuando está habilitado para usuario"""
    user = User(id=1, tarea_email=True, tarea_push=False, token_fcm="fcm_token_123")
    notification = UserNotificationEvent(**user_notification_data)
    
    await send_notifications(user, 1, "test@test.com", notification, "Asunto", "Cuerpo")
    
    # Verificar que se envió email
    mock_email_service.assert_called_once_with("test@test.com", "Asunto", "Cuerpo")
    # Verificar que NO se envió push
    mock_push_service.assert_not_called()
    # Verificar que se creó log de email
    mock_log_repository.assert_called_once()


@pytest.mark.asyncio
async def test_send_notifications_user_push_enabled(self, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica que se envía push cuando está habilitado para usuario"""
    user = User(id=1, tarea_email=False, tarea_push=True, token_fcm="fcm_token_123")
    notification = UserNotificationEvent(**user_notification_data)
    
    await send_notifications(user, 1, "test@test.com", notification, "Asunto", "Cuerpo")
    
    # Verificar que NO se envió email
    mock_email_service.assert_not_called()
    # Verificar que se envió push
    mock_push_service.assert_called_once_with("fcm_token_123", "Asunto", "Cuerpo")
    # Verificar que se creó log de push
    mock_log_repository.assert_called_once()


@pytest.mark.asyncio
async def test_send_notifications_user_both_disabled(self, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica que no se envían notificaciones cuando ambas están deshabilitadas"""
    user = User(id=1, tarea_email=False, tarea_push=False, token_fcm="fcm_token_123")
    notification = UserNotificationEvent(**user_notification_data)
    
    await send_notifications(user, 1, "test@test.com", notification, "Asunto", "Cuerpo")
    
    # Verificar que NO se envió email
    mock_email_service.assert_not_called()
    # Verificar que NO se envió push
    mock_push_service.assert_not_called()
    # Verificar que NO se crearon logs
    mock_log_repository.assert_not_called()


@pytest.mark.asyncio
async def test_process_user_notification_success(self, mock_user_repository, mock_user_service, mock_format_notification, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica el procesamiento exitoso de notificación de usuario"""
    user = User(id=1, tarea_email=True, tarea_push=True, token_fcm="fcm_token_123")
    mock_user_repository["get"].return_value = user
    mock_user_service.return_value = user_info_data
    
    notification = UserNotificationEvent(**user_notification_data)
    
    await process_user_notification(notification)
    
    # Verificar que se obtuvieron las preferencias del usuario
    mock_user_repository["get"].assert_called_once()
    # Verificar que se obtuvo información del usuario
    mock_user_service.assert_called_once_with(1)
    # Verificar que se formateó la notificación
    mock_format_notification.assert_called_once()
    # Verificar que se enviaron notificaciones
    mock_email_service.assert_called_once()
    mock_push_service.assert_called_once()


@pytest.mark.asyncio
async def test_process_user_notification_user_info_error(self, mock_user_repository, mock_user_service):
    """Test que verifica el manejo de error al obtener información del usuario"""
    user = User(id=1)
    mock_user_repository["get"].return_value = user
    mock_user_service.side_effect = Exception("Error al obtener usuario")
    
    notification = UserNotificationEvent(**user_notification_data)
    
    with pytest.raises(HTTPException) as exc_info:
        await process_user_notification(notification)
    
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_process_course_notification_success(self, mock_courses_service, mock_user_service, mock_user_repository, mock_format_notification, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica el procesamiento exitoso de notificación de curso"""
    user_list = [1, 2, 3]
    mock_courses_service.return_value = user_list
    mock_user_service.return_value = user_info_data
    
    user = User(id=1, tarea_email=True, tarea_push=True, token_fcm="fcm_token_123")
    mock_user_repository["get"].return_value = user
    
    notification = CourseNotificationEvent(**course_notification_data)
    
    await process_course_notification(notification)
    
    # Verificar que se obtuvieron los usuarios del curso
    mock_courses_service.assert_called_once_with("curso-123")
    # Verificar que se proceso cada usuario
    assert mock_user_service.call_count == 3
    assert mock_format_notification.call_count == 3


@pytest.mark.asyncio
async def test_process_course_notification_no_users(self, mock_courses_service):
    """Test que verifica el manejo cuando no hay usuarios en el curso"""
    mock_courses_service.return_value = []
    
    notification = CourseNotificationEvent(**course_notification_data)
    
    with pytest.raises(HTTPException) as exc_info:
        await process_course_notification(notification)
    
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_process_course_notification_user_info_error_continues(self, mock_courses_service, mock_user_service, mock_user_repository, mock_format_notification):
    """Test que verifica que continúa procesando otros usuarios si falla uno"""
    user_list = [1, 2, 3]
    mock_courses_service.return_value = user_list
    mock_user_service.side_effect = [Exception("Error"), user_info_data, user_info_data]
    
    user = User(id=1, tarea_email=True, tarea_push=True, token_fcm="fcm_token_123")
    mock_user_repository["get"].return_value = user
    
    notification = CourseNotificationEvent(**course_notification_data)
    
    # No debería lanzar excepción, debería continuar con los otros usuarios
    await process_course_notification(notification)
    
    # Verificar que se intentó procesar todos los usuarios
    assert mock_user_service.call_count == 3
    # Verificar que se formateó para los usuarios exitosos
    assert mock_format_notification.call_count == 2


@pytest.mark.asyncio
async def test_process_aux_teacher_notification_success(self, mock_user_repository, mock_user_service, mock_format_notification, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica el procesamiento exitoso de notificación de docente auxiliar"""
    user = User(id=1, token_fcm="fcm_token_123")
    mock_user_repository["get"].return_value = user
    mock_user_service.return_value = user_info_data
    
    notification = AuxiliaryTeacherNotificationEvent(**auxiliary_teacher_data)
    
    await process_aux_teacher_notification(notification)
    
    # Verificar que se obtuvieron las preferencias del usuario
    mock_user_repository["get"].assert_called_once()
    # Verificar que se obtuvo información del usuario
    mock_user_service.assert_called_once_with(1)
    # Verificar que se formateó la notificación
    mock_format_notification.assert_called_once()
    # Verificar que se enviaron notificaciones (siempre para aux teacher)
    mock_email_service.assert_called_once()
    mock_push_service.assert_called_once()


@pytest.mark.asyncio
async def test_process_aux_teacher_notification_user_info_error(self, mock_user_repository, mock_user_service):
    """Test que verifica el manejo de error al obtener información del docente auxiliar"""
    user = User(id=1)
    mock_user_repository["get"].return_value = user
    mock_user_service.side_effect = Exception("Error al obtener usuario")
    
    notification = AuxiliaryTeacherNotificationEvent(**auxiliary_teacher_data)
    
    with pytest.raises(HTTPException) as exc_info:
        await process_aux_teacher_notification(notification)
    
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_process_message_user_notification(self, mock_user_repository, mock_user_service, mock_format_notification, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica el procesamiento de mensaje de notificación de usuario"""
    user = User(id=1, tarea_email=True, tarea_push=True, token_fcm="fcm_token_123")
    mock_user_repository["get"].return_value = user
    mock_user_service.return_value = user_info_data
    
    message_body = json.dumps(user_notification_data).encode('utf-8')
    
    await process_message(message_body)
    
    # Verificar que se procesó la notificación
    mock_user_service.assert_called_once()
    mock_format_notification.assert_called_once()


@pytest.mark.asyncio
async def test_process_message_course_notification(self, mock_courses_service, mock_user_service, mock_user_repository, mock_format_notification, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica el procesamiento de mensaje de notificación de curso"""
    user_list = [1]
    mock_courses_service.return_value = user_list
    mock_user_service.return_value = user_info_data
    
    user = User(id=1, tarea_email=True, tarea_push=True, token_fcm="fcm_token_123")
    mock_user_repository["get"].return_value = user
    
    message_body = json.dumps(course_notification_data).encode('utf-8')
    
    await process_message(message_body)
    
    # Verificar que se procesó la notificación
    mock_courses_service.assert_called_once()
    mock_user_service.assert_called_once()


@pytest.mark.asyncio
async def test_process_message_aux_teacher_notification(self, mock_user_repository, mock_user_service, mock_format_notification, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica el procesamiento de mensaje de notificación de docente auxiliar"""
    user = User(id=1, token_fcm="fcm_token_123")
    mock_user_repository["get"].return_value = user
    mock_user_service.return_value = user_info_data
    
    message_body = json.dumps(auxiliary_teacher_data).encode('utf-8')
    
    await process_message(message_body)
    
    # Verificar que se procesó la notificación
    mock_user_service.assert_called_once()
    mock_format_notification.assert_called_once()


@pytest.mark.asyncio
async def test_process_message_invalid_event_type(self):
    """Test que verifica el manejo de tipo de evento inválido"""
    invalid_data = {
        "event_type": "invalid_type",
        "id_user": 1
    }
    message_body = json.dumps(invalid_data).encode('utf-8')
    
    # No debería lanzar excepción, solo loggear error
    await process_message(message_body)


@pytest.mark.asyncio
async def test_process_message_invalid_json(self):
    """Test que verifica el manejo de JSON inválido"""
    invalid_message = b"invalid json"
    
    # No debería lanzar excepción, solo loggear error
    await process_message(invalid_message)


@pytest.mark.asyncio
async def test_process_message_exception_handling(self):
    """Test que verifica el manejo de excepciones generales"""
    message_body = json.dumps(user_notification_data).encode('utf-8')
    
    with patch("app.services.notification_processor.process_user_notification") as mock_process:
        mock_process.side_effect = Exception("Error general")
        
        # No debería lanzar excepción, solo loggear error
        await process_message(message_body)


@pytest.mark.asyncio
async def test_send_notifications_without_fcm_token(self, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica el comportamiento cuando no hay token FCM"""
    user = User(id=1, tarea_email=False, tarea_push=True, token_fcm=None)
    notification = UserNotificationEvent(**user_notification_data)
    
    await send_notifications(user, 1, "test@test.com", notification, "Asunto", "Cuerpo")
    
    # Verificar que NO se envió push (porque no hay token)
    mock_push_service.assert_not_called()
    # Verificar que NO se creó log
    mock_log_repository.assert_not_called()


@pytest.mark.asyncio
async def test_send_notifications_empty_fcm_token(self, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica el comportamiento con token FCM vacío"""
    user = User(id=1, tarea_email=False, tarea_push=True, token_fcm="")
    notification = UserNotificationEvent(**user_notification_data)
    
    await send_notifications(user, 1, "test@test.com", notification, "Asunto", "Cuerpo")
    
    # Verificar que se intentó enviar push (aunque falle)
    mock_push_service.assert_called_once_with("", "Asunto", "Cuerpo")
    # Verificar que NO se creó log (porque falló)
    mock_log_repository.assert_not_called()


@pytest.mark.asyncio
async def test_process_user_notification_create_user_if_not_exists(self, mock_user_repository, mock_user_service, mock_format_notification, mock_email_service, mock_push_service, mock_log_repository, mock_session_local):
    """Test que verifica que se crea usuario si no existe"""
    new_user = User(id=1, tarea_email=True, tarea_push=True, token_fcm="fcm_token_123")
    mock_user_repository["get"].return_value = None
    mock_user_repository["create"].return_value = new_user
    mock_user_service.return_value = user_info_data
    
    notification = UserNotificationEvent(**user_notification_data)
    
    await process_user_notification(notification)
    
    # Verificar que se intentó obtener usuario
    mock_user_repository["get"].assert_called_once()
    # Verificar que se creó usuario
    mock_user_repository["create"].assert_called_once()
    # Verificar que se procesó la notificación
    mock_user_service.assert_called_once() 