import pytest
from fastapi import HTTPException, status
from app.models.user import User


def test_get_user_preferences_success(client, mock_auth_service, db_session):
    mock_auth_service.return_value = 1
    user = User(
        id=1, examen_email=True, examen_push=False, tarea_email=False, tarea_push=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.get(
        "/me/preferences", headers={"Authorization": "Bearer valid_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["examen_email"] is True
    assert data["examen_push"] is False
    assert data["tarea_email"] is False
    assert data["tarea_push"] is True


def test_get_user_preferences_unauthorized(client, mock_auth_service):
    mock_auth_service.return_value = None

    response = client.get(
        "/me/preferences", headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_preferences_not_found(client, mock_auth_service, db_session):
    mock_auth_service.return_value = 999  # ID que no existe

    response = client.get(
        "/me/preferences", headers={"Authorization": "Bearer valid_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 999
    assert data["examen_email"] is True  # Valores por defecto
    assert data["examen_push"] is True
    assert data["tarea_email"] is True
    assert data["tarea_push"] is True


def test_edit_user_preferences_success(client, mock_auth_service, db_session):
    mock_auth_service.return_value = 1
    user = User(id=1)
    db_session.add(user)
    db_session.commit()

    new_preferences = {
        "examen_email": True,
        "examen_push": False,
        "tarea_email": True,
        "tarea_push": True,
    }

    response = client.put(
        "/me/editpreferences",
        headers={"Authorization": "Bearer valid_token"},
        json=new_preferences,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["examen_email"] is True
    assert data["examen_push"] is False
    assert data["tarea_email"] is True
    assert data["tarea_push"] is True


def test_edit_user_preferences_unauthorized(client, mock_auth_service):
    mock_auth_service.return_value = None

    response = client.put(
        "/me/editpreferences",
        headers={"Authorization": "Bearer invalid_token"},
        json={},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_edit_user_preferences_not_found(client, mock_auth_service, db_session):
    mock_auth_service.return_value = 999  # ID que no existe

    response = client.put(
        "/me/editpreferences",
        headers={"Authorization": "Bearer valid_token"},
        json={
            "examen_email": True,
            "examen_push": False,
            "tarea_email": True,
            "tarea_push": True,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


fcm_token_data = {"fcm_token": "fcm_token_example_12345"}


def test_edit_fcm_token_success(client, mock_auth_service, db_session):
    mock_auth_service.return_value = 1

    response = client.put(
        "/me/editfcmtoken",
        headers={"Authorization": "Bearer valid_token"},
        json=fcm_token_data,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["token_fcm"] == fcm_token_data["fcm_token"]


def test_edit_fcm_token_unauthorized(client, mock_auth_service):
    mock_auth_service.return_value = None

    response = client.put(
        "/me/editfcmtoken",
        headers={"Authorization": "Bearer invalid_token"},
        json=fcm_token_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
