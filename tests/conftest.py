import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.dependencies import get_db
from unittest.mock import patch, MagicMock

# Crear una base de datos en memoria para testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_auth_service():
    with patch("app.controller.user_controller.validate_user") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_courses_service():
    with patch("app.services.notification_processor.get_course_users") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_email_service():
    with patch("app.services.notification_processor.send_email") as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_queue_repository():
    with patch(
        "app.controller.notification_controller.QueueRepository"
    ) as mock1, patch("app.workers.notification_worker.QueueRepository") as mock2:
        mock_instance = MagicMock()
        mock1.return_value = mock_instance
        mock2.return_value = mock_instance
        yield mock_instance
