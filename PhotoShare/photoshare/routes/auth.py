from typing import List
from fastapi import (
    APIRouter, HTTPException, Depends, status,
    Security, BackgroundTasks, Request
)
from fastapi.security import (
    OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
)
from sqlalchemy.orm import Session
from photoshare.database.db import get_db
from photoshare.schemas import UserModel, UserResponse, TokenModel, UserDb
from photoshare.repository import users as repository_users
from photoshare.database.models import User
from photoshare.services.auth import auth_service
# from photoshare.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint to sign up a new user.

    :param body: The user data.
    :param background_tasks: Background tasks to be executed.
    :param request: The request object.
    :param db: The database session. Defaults to Depends(get_db).
    :return: The response containing the created user.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already use"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint to authenticate and log in a user.

    :param body: The login form data.
    :param db: The database session. Defaults to Depends(get_db).
    :raise HTTPException: If the email or password is invalid or user is inactive.
    :return: The response containing the access and refresh tokens and token type.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(
        data={"sub": user.email}
    )
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": user.email}
    )
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """
    Endpoint to refresh an access token.

    :param credentials: The HTTP authorization credentials.
    :param db: The database session. Defaults to Depends(get_db).
    :return: The response containing the new access and refresh tokens and token type.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(
        data={"sub": email}
    )
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
