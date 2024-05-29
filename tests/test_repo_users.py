import pytest
from sqlalchemy.orm import Session
from photoshare_src.database.models import User, Image
from photoshare_src.database.models import Base
from photoshare_src.schemas import UserModel, UserUpdate
from photoshare_src.repository.users import (
    create_user,
    get_user_by_email,
    update_token,
    update_user_role,
    set_user_active_status,
    get_user_by_username,
    update_user_info,
)
from photoshare_src.database.db import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from main import app
from fastapi.testclient import TestClient


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
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


@pytest.mark.asyncio
async def test_create_user(db_session: Session):
    # Подготовка
    user_data = UserModel(username="test_user", email="test@example.com", password="password")
    
    # Действие
    created_user = await create_user(user_data, db_session)
    
    # Проверка
    assert created_user
    assert created_user.username == user_data.username
    assert created_user.email == user_data.email
    assert created_user.role == "admin"  # Первый созданный пользователь должен быть администратором


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: Session):
    # Подготовка
    email = "test@example.com"
    
    # Действие
    retrieved_user = await get_user_by_email(email, db_session)
    
    # Проверка
    assert retrieved_user
    assert retrieved_user.email == email


@pytest.mark.asyncio
async def test_update_token(db_session: Session):
    # Подготовка
    email = "test@example.com"
    
    # Действие
    user = await get_user_by_email(email, db_session)
    new_token = "new_refresh_token"
    
    # Действие
    await update_token(user, new_token, db_session)
    updated_user = await get_user_by_email(user.email, db_session)
    
    # Проверка
    assert updated_user
    assert updated_user.refresh_token == new_token


@pytest.mark.asyncio
async def test_update_user_role(db_session: Session):
    email = "test@example.com"
    user = await get_user_by_email(email, db_session)

    new_role = "user"

    updated_user = await update_user_role(db_session, user.id, new_role)
    
    # Проверка
    assert updated_user
    assert updated_user.role == new_role


@pytest.mark.asyncio
async def test_set_user_active_status(db_session: Session):
    # Подготовка
    email = "test@example.com"
    user = await get_user_by_email(email, db_session)
    
    # Действие
    updated_user = set_user_active_status(db_session, user.id, True)
    
    # Проверка
    assert updated_user
    assert updated_user.is_active


@pytest.mark.asyncio
async def test_get_user_by_username(db_session: Session):
    # Подготовка
    username = "test_user"
    
    # Действие
    retrieved_user, image_count = get_user_by_username(db_session, username)
    
    # Проверка
    assert retrieved_user
    assert retrieved_user.username == username
    assert image_count == 0  # Поскольку пользователь только что создан, у него нет изображений


@pytest.mark.asyncio
async def test_update_user_info(db_session: Session):
    # Подготовка
    email = "test@example.com"
    user = await get_user_by_email(email, db_session)
    new_username = "updated_username"
    new_email = "updated@example.com"
    new_password = "updated_password"
    user_update_data = UserUpdate(username=new_username, email=new_email, password=new_password)
    
    # Действие
    updated_user = await update_user_info(db_session, user_update_data, user)
    
    # Проверка
    assert updated_user
    assert updated_user.username == new_username
    assert updated_user.email == new_email
    # В реальном приложении может потребоваться проверка пароля
