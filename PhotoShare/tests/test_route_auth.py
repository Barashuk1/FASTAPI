import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from photoshare.services.auth import auth_service
from photoshare.repository.users import create_user, get_user_by_email


@pytest.fixture(scope="module")
def admin_user(session: Session, admin_user_data):
    user_data = admin_user_data.copy()
    user_data["password"] = auth_service.get_password_hash(user_data["password"])
    db_user = create_user(session, user_data)
    session.commit()
    return db_user

@pytest.mark.asyncio
async def test_signup(client: TestClient, session: Session, test_user_data):
    response = client.post("/api/auth/signup", json=test_user_data)
    print(response.json())  # Debugging line
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == test_user_data["email"]

    # Ensure the user is created in the database
    user = await get_user_by_email(test_user_data["email"], session)
    assert user is not None
    assert auth_service.verify_password(test_user_data["password"], user.password)

@pytest.mark.asyncio
async def test_login(client: TestClient, session: Session, test_user_data):
    # Ensure the user is created before trying to login
    user = await get_user_by_email(test_user_data["email"], session)
    if not user:
        # Create the user if it doesn't exist
        user_data = test_user_data.copy()
        user_data["password"] = auth_service.get_password_hash(user_data["password"])
        create_user(session, user_data)
        session.commit()

    response = client.post("/api/auth/login", data={"username": test_user_data["email"], "password": test_user_data["password"]})
    print(response.json())  # Debugging line
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    return data  # Return tokens for further tests

def test_invalid_login(client: TestClient):
    response = client.post("/api/auth/login", data={"username": "invalid@example.com", "password": "wrongpassword"})
    print(response.json())  # Debugging line
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email"  # Adjusted to the actual error message

@pytest.mark.asyncio
async def test_refresh_token(client: TestClient, session: Session, test_user_data):
    login_data = await test_login(client, session, test_user_data)
    refresh_token = login_data["refresh_token"]
    headers = {"Authorization": f"Bearer {refresh_token}"}

    response = client.get("/api/auth/refresh_token", headers=headers)
    print(response.json())  # Debugging line
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_invalid_refresh_token(client: TestClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/api/auth/refresh_token", headers=headers)
    print(response.json())  # Debugging line
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Could not validate credentials"
