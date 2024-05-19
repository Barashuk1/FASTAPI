from photoshare.database.db import Session
from photoshare.database.models import Image, User
from photoshare.schemas import *
from fastapi import HTTPException


def load_image_func(db: Session, image: ImageCreate, user: User) -> ImageDB:
    db_image = Image(**image.model_dump())
    db_image.user_id = user.id
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def delete_image_func(db: Session, image_id: int, user: User) -> ImageDB:
    if user.role == "admin":
        db_image = db.query(Image).filter(Image.id == image_id).first()
    else:
        db_image = db.query(Image).filter(Image.id == image_id, Image.user_id == user.id).first()
        if not db_image:
            # Якщо зображення не знайдено або не належить поточному користувачу, викинути виняток HTTP 404
            raise HTTPException(status_code=404, detail="Image not found or you don't have permission to delete it.")
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image


def update_image_func(db: Session, image_id: int, image: ImageUpdate, user: User) -> ImageDB:
    if user.role == "admin":
        db_image = db.query(Image).filter(Image.id == image_id).first()
    else:
        db_image = db.query(Image).filter(Image.id == image_id, Image.user_id == user.id).first()
        if not db_image:
            # Якщо зображення не знайдено або не належить поточному користувачу, викинути виняток HTTP 404
            raise HTTPException(status_code=404, detail="Image not found or you don't have permission to delete it.")
    if db_image:
        for key, val in image.model_dump().items():
            setattr(db_image, key, val)
        db.commit()
        db.refresh(db_image)
    return db_image


def get_image_url_func(db: Session, url_view: str) -> ImageDB:
    db_image = db.query(Image).filter(Image.url_view == url_view).first()
    return db_image


def get_image_func(db: Session, image_id: int) -> ImageDB:
    db_image = db.query(Image).filter(Image.id == image_id).first()
    return db_image
