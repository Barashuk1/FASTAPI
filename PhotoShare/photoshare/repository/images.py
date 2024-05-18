from photoshare.database.db import Session
from photoshare.database.models import Image
from photoshare.schemas import ImageBase

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