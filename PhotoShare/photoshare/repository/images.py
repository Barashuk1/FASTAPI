from photoshare.database.db import Session
from photoshare.database.models import Image
from photoshare.schemas import *


def load_image_func(db: Session, image: ImageBase) -> ImageDB:
    db_image = Image(**image.model_dump())
    db_image.user_id = 1    # temporary
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def delete_image_func(db: Session, image_id: int) -> ImageDB:
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image


def update_image_func(db: Session, image_id: int, image: ImageUpdate) -> ImageDB:
    db_image = db.query(Image).filter(Image.id == image_id).first()
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


def rate_images_func(db: Session, order: str) -> list[ImageDB]:
    if order == "asc":
        return db.query(Image).order_by(Image.rate.asc()).all()
    else:
        return db.query(Image).order_by(Image.rate.desc()).all()
