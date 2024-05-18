from photoshare.database.db import Session
from photoshare.database.models import Image
from photoshare.schemas import *

def load_image_func(db: Session, image: ImageBase):
    db_image = Image(**image.dict())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def delete_image_func(db: Session, image_id: int):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image

def update_image_func(db: Session, image_id: int, image: ImageUpdate):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if db_image:
        for key, val in image.dict().items():
            setattr(db_image, key, val)
        db.commit()
        db.refresh()
    return db_image

def get_image_url_func(db: Session, url_view: str):
    db_image = db.query(Image).filter(Image.url_view == url_view).first()
    return db_image

def get_image_func(db: Session, image_id: int):
    db_image = db.query(Image).filter(Image.id == image_id).first()
    return db_image
    
