import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from photoshare_src.database.models import User
from photoshare_src.services.auth import Auth

# Моделюємо залежності
class MockDB:
    def __init__(self, user=None):
        self.user = user
    
    def __call__(self):
        return self
    
    async def get_user_by_email(self, email, db):
        if self.user and self.user.email == email:
            return self.user
        return None
    
    def query(self, model):
        return self
    
    def filter(self, condition):
        return self
    
    # Метод для эмуляции метода first
    async def first(self):
        # Возвращаем первый элемент, в данном случае, просто возвращаем user
        return self.user




@pytest.fixture
def mock_db():
    return MockDB()

@pytest.fixture
def auth_service():
    return Auth()

@pytest.mark.asyncio
async def test_decode_refresh_token(auth_service):
    data = {"sub": "test@example.com"}
    refresh_token = await auth_service.create_refresh_token(data)
    email = await auth_service.decode_refresh_token(refresh_token)
    assert email == "test@example.com"

@pytest.mark.asyncio
async def test_get_current_user(mock_db, auth_service):
    user = User(id=1, email="test@example.com", password="password")
    mock_db = MockDB(user=user)
    token = await auth_service.create_access_token({"sub": user.email})
    print(token)
    current_user = await auth_service.get_current_user(token, db=mock_db)
    print(current_user)
    current_user_data = await current_user  # Await the coroutine to get the actual user object
    print(current_user_data)
    assert current_user_data.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_current_user_raises_unauthorized(mock_db, auth_service):
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.get_current_user("invalid_token", db=mock_db)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_current_user_raises_unauthorized_no_email(mock_db, auth_service):
    token = await auth_service.create_access_token({"sub": None})
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.get_current_user(token, db=mock_db)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_current_user_roles(auth_service):
    user = User(id=1, email="test@example.com", password="password", role="admin")
    required_roles = ["admin"]
    verifier = auth_service.get_current_user_roles(required_roles)
    result = await verifier(current_user=user)
    assert result == user

@pytest.mark.asyncio
async def test_get_current_user_roles_raises_forbidden(auth_service):
    user = User(id=1, email="test@example.com", password="password", role="user")
    required_roles = ["admin"]
    verifier = auth_service.get_current_user_roles(required_roles)
    with pytest.raises(HTTPException) as exc_info:
        await verifier(current_user=user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
