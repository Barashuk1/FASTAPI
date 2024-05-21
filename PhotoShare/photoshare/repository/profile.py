from sqlalchemy.orm import Session
from photoshare.database.models import User, Image
from sqlalchemy import func
from photoshare.schemas import *
from fastapi import HTTPException

def get_user_by_username(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        images_count = db.query(func.count(Image.id)).filter(Image.user_id == user.id).scalar()
        return user, images_count
    return None

def update_user_info(db: Session, user_update: UserUpdate, user: User) -> User:
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