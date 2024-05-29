from sqlalchemy.orm import Session
from photoshare_src.database.models import User, Image
from photoshare_src.schemas import UserModel
from sqlalchemy import func
from photoshare_src.schemas import *
from fastapi import HTTPException


async def get_user_by_email(
    email: str,
    db: Session
) -> User:
    """
    Retrieve a user by email from the database.

    :param email: The email address of the user to retrieve.
    :param db: The database session.
    :return: The retrieved user.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(
    body: UserModel,
    db: Session
) -> User:
    """
    Create a new user in the database.

    :param body: The user data.
    :param db: The database session.
    :return: The created user.
    """
    user_count = db.query(User).count()
    new_user = User(**body.dict())
    new_user.role = 'admin' if user_count == 0 else 'user'
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(
    user: User,
    token: str | None,
    db: Session
) -> None:
    """
    Update the refresh token for a user.

    :param user: The user whose token is being updated.
    :param token: The new refresh token, or None if no token is provided.
    :param db: The database session.
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def update_user_role(
    db: Session,
    user_id: int,
    role: str
) -> User:
    """
    Function to update user role in the database

    :param db: SQLAlchemy session
    :param user_id: id of the user
    :param role: new role
    :return: User object
    """
    user = db.query(User).filter(User.id == user_id).first()
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def set_user_active_status(
    db: Session,
    user_id: int,
    is_active: bool
) -> User:
    """
    Function to set user active status in the database

    :param db: SQLAlchemy session
    :param user_id: id of the user
    :param is_active: new active status
    :return: User object
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(
    db: Session,
    username: str
) -> tuple[User, int] | None:
    """
    Function to get user by username from the database

    :param db: SQLAlchemy session
    :param username: username
    :return: User object and number of images uploaded by the user or None
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        images_count = db.query(func.count(Image.id)).filter(
            Image.user_id == user.id
        ).scalar()
        return user, images_count
    return None


async def update_user_info(
    db: Session,
    user_update: UserUpdate,
    user: User
) -> User:
    """
    Function to update user info in the database

    :param db: SQLAlchemy session
    :param user_update: UserUpdate object
    :param user: User object
    :raise HTTPException: if user not found
    :return: User object
    """
    user = db.query(User).filter(User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found.")
    if user:
        user.username = user_update.username
        user.email = user_update.email
        user.password = user_update.password
        db.commit()
        db.refresh(user)
        return user

