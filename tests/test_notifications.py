import pytest
from fastapi import HTTPException, status
from app.models.user import User

user_notification_data = {
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

course_notification_data = {
    "id_course": "curso-123",
    "notification_type": "Tarea",
    "event": "Nuevo",
    "data": {
        "titulo": "Tarea 1",
        "descripcion": "Descripción de la tarea",
        "fecha": "2024-03-20",
    },
}


def test_create_user_notification_success(
    client, mock_auth_service, mock_queue_repository, db_session
):
    mock_auth_service.return_value = 1
    mock_queue_repository.send_message.return_value = True

    response = client.post(
        "/notify/user",
        headers={"Authorization": "Bearer valid_token"},
        json=user_notification_data,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


def test_create_user_notification_unauthorized(client, mock_auth_service):
    mock_auth_service.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
    )

    response = client.post(
        "/notify/user",
        headers={"Authorization": "Bearer invalid_token"},
        json=user_notification_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_user_notification_queue_error(
    client, mock_auth_service, mock_queue_repository
):
    mock_auth_service.return_value = 1
    mock_queue_repository.send_message.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error interno del servidor",
    )

    response = client.post(
        "/notify/user",
        headers={"Authorization": "Bearer valid_token"},
        json=user_notification_data,
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_create_course_notification_success(
    client, mock_auth_service, mock_queue_repository
):
    mock_auth_service.return_value = 1
    mock_queue_repository.send_message.return_value = True

    response = client.post(
        "/notify/course",
        headers={"Authorization": "Bearer valid_token"},
        json=course_notification_data,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


def test_create_course_notification_unauthorized(client, mock_auth_service):
    mock_auth_service.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
    )

    response = client.post(
        "/notify/course",
        headers={"Authorization": "Bearer invalid_token"},
        json=course_notification_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_course_notification_queue_error(
    client, mock_auth_service, mock_queue_repository
):
    mock_auth_service.return_value = 1
    mock_queue_repository.send_message.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error interno del servidor",
    )

    response = client.post(
        "/notify/course",
        headers={"Authorization": "Bearer valid_token"},
        json=course_notification_data,
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
