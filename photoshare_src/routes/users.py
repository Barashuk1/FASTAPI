from fastapi import FastAPI, Depends,  APIRouter, HTTPException, status
from photoshare_src.schemas import *
from photoshare_src.database.db import Session, get_db
from photoshare_src.services.auth import auth_service
from photoshare_src.repository.users import *

router = APIRouter(prefix='/user', tags=["user"])

@router.get("/{username}", response_model=UserProfile)
def get_user_profile(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Get a user profile by username

    :param username: The username of the user to retrieve
    :param db: Database session
    :return: The user profile
    """
    user, images_count = get_user_by_username(db, username)
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "images_count": images_count
    }
    return user_data

@router.put("/{username}/settings", response_model=UserResponse)
async def update_user(
    body: UserModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Update user settings

    :param body: The user data to update
    :param db: Database session
    :param current_user: The current user
    :raise HTTPException: If the email is already in use
    :return: The updated user
    """
    if body.email != current_user.email:
        exist_user = await get_user_by_email(body.email, db)
        if exist_user and exist_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await update_user_info(db, body, current_user)
    return {"user": new_user, "detail": "User successfully created"}


@router.put("/admin/{user_id}/role", response_model=UserResponse)
async def set_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        auth_service.get_current_user_roles(["admin"])
    )
):
    """
    Set a user role

    :param user_id: The ID of the user to update
    :param role: The role to set
    :param db: Database session
    :param current_admin: The current admin user
    :raise HTTPException: If the role is invalid
    :return: The updated user
    """
    if role not in ["user", "moderator"]:
        raise HTTPException(
            status_code=400, detail="Invalid role, use 'user', 'moderator'"
        )
    user = await update_user_role(db, user_id, role)
    return {"user": user, "detail": "User successfully update"}


@router.put("/admin/{user_id}/ban", response_model=UserResponse)
async def ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        auth_service.get_current_user_roles(["admin"])
    )
):
    """
    Ban a user

    :param user_id: The ID of the user to ban
    :param db: Database session
    :param current_admin: The current admin user
    :raise HTTPException: If the user is not found
    :return: The updated user
    """
    user = set_user_active_status(db, user_id, is_active=False)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/admin/{user_id}/unban", response_model=UserResponse)
async def unban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(
        auth_service.get_current_user_roles(["admin"])
    )
):
    """
    Unban a user

    :param user_id: The ID of the user to unban
    :param db: Database session
    :param current_admin: The current admin user
    :raise HTTPException: If the user is not found
    :return: The updated user
    """
    user = set_user_active_status(db, user_id, is_active=True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
