from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from photoshare.database.db import get_db
from photoshare.schemas import UserModel, UserResponse, TokenModel
from photoshare.repository import users as repository_users
from photoshare.database.models import User
from photoshare.services.auth import auth_service
# from photoshare.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Endpoint to sign up a new user.

    Parameters:
    - body (UserModel): The user data.
    - background_tasks (BackgroundTasks): Background tasks to be executed.
    - request (Request): The request object.
    - db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    - UserResponse: The response containing the created user.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint to authenticate and log in a user.

    Parameters:
    - body (OAuth2PasswordRequestForm): The login form data.
    - db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    - TokenModel: The response containing the access and refresh tokens.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Endpoint to refresh an access token.

    Parameters:
    - credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials.
    - db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
    - TokenModel: The response containing the new access and refresh tokens.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def set_user_role(user_id: int, role: str, db: Session = Depends(get_db),
                      current_admin: User = Depends(auth_service.get_current_user_roles(["admin"]))):
    if role not in ["user", "moderator"]:
        raise HTTPException(status_code=400, detail="Invalid role, use 'user', 'moderator'")
    user = await repository_users.update_user_role(db, user_id, role)
    return {"user": user, "detail": "User successfully update"}


# @router.get('/confirmed_email/{token}')
# async def confirmed_email(token: str, db: Session = Depends(get_db)):
#     """
#     Endpoint to confirm a user's email.

#     Parameters:
#     - token (str): The email confirmation token.
#     - db (Session, optional): The database session. Defaults to Depends(get_db).

#     Returns:
#     - dict: A message indicating the status of the email confirmation.
#     """
#     email = await auth_service.get_email_from_token(token)
#     user = await repository_users.get_user_by_email(email, db)
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
#     if user.confirmed:
#         return {"message": "Your email is already confirmed"}
#     await repository_users.confirmed_email(email, db)
#     return {"message": "Email confirmed"}


# @router.post('/request_email')
# async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
#                         db: Session = Depends(get_db)):
#     """
#     Endpoint to request a confirmation email.

#     Parameters:
#     - body (RequestEmail): The request data containing the user's email.
#     - background_tasks (BackgroundTasks): Background tasks to be executed.
#     - request (Request): The request object.
#     - db (Session, optional): The database session. Defaults to Depends(get_db).

#     Returns:
#     - dict: A message indicating the status of the email request.
#     """
#     user = await repository_users.get_user_by_email(body.email, db)

#     if user.confirmed:
#         return {"message": "Your email is already confirmed"}
#     if user:
#         background_tasks.add_task(
#             send_email, user.email, user.username, request.base_url)
#     return {"message": "Check your email for confirmation."}
