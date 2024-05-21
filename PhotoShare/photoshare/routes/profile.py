from fastapi import FastAPI, Depends,  APIRouter
from photoshare.schemas import *
from photoshare.database.db import Session, get_db
from photoshare.services.auth import auth_service
from photoshare.repository.profile import *

router = APIRouter(prefix='/user', tags=["user"])

@router.get("/{username}", response_model=UserProfile)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    user, images_count = get_user_by_username(db, username)  
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "images_count": images_count
    }
    return user_data

@router.put("/{username}/settings", response_model=UserModel)
def update_user(user_update: UserUpdate, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    return update_user_info(db, user_update, current_user)

