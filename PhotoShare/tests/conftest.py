import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from main import app
from photoshare.database.models import Base
from photoshare.database.models import User
from photoshare.database.db import get_db
from photoshare.repository.users import create_user, get_user_by_email
from photoshare.services.auth import auth_service
from unittest.mock import MagicMock

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def test_user_data():
    return {"username": "testuser12", "email": "testuser@example.com", "password": "testpass12"}


@pytest.fixture(scope="module")
def admin_user_data():
    return {"username": "adminadmin", "email": "admin@example.com", "password": "adminpass"}

@pytest.fixture(scope="module")
def admin_user(session: Session, admin_user_data):
    # Create admin user
    user_data = admin_user_data.copy()
    user_data["password"] = auth_service.get_password_hash(user_data["password"])
    db_user = create_user(session, user_data)
    session.commit()
    return db_user



