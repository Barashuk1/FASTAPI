from photoshare.database.db import Session
from photoshare.database.models import Image, User, Tag
from photoshare.schemas import *
from fastapi import HTTPException
from fastapi import FastAPI, File, UploadFile
from sqlalchemy import and_

import cloudinary
import cloudinary.uploader
from cloudinary import CloudinaryImage
from io import BytesIO
import re
import qrcode
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styledpil import StyledPilImage

cloudinary.config(
    cloud_name='dxnanxzgt',
    api_key='624561594715217',
    api_secret='SuZE2oky-Kq8xEEt53G1h9zS-pg'
)



def load_image_func(db: Session, image: ImageBase, tags: List[str], user: User) -> ImageDB:
    image_tags = []
    for tag_name in tags:
        # Перевіряємо, чи існує тег з такою назвою
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            # Якщо тега не існує, створюємо новий
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        image_tags.append(tag)


    db_image = Image(**image.model_dump())
    db_image.user_id = user.id
    db_image.tags = image_tags
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def load_image_from_pc_func( db: Session, description, user: User, file: UploadFile = File(), tags: Optional[str] = None):
    upload_result = cloudinary.uploader.upload(
    file.file,
    overwrite=True
)
    if tags:
        try:
            tags_list = tags.split(",") 
            image_tags = []
            for tag_name in tags_list:
                # Перевіряємо, чи існує тег з такою назвою
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    # Якщо тега не існує, створюємо новий
                    tag = Tag(name=tag_name.strip())
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)
                image_tags.append(tag)
        except:
            raise HTTPException(status_code=400, detail="Uncorrect fromat of tags")

    image_url = upload_result["url"]
    print("image_url", image_url)
    new_image = Image()
    new_image.url = image_url
    new_image.description = description
    new_image.created_at = datetime.now()
    new_image.user_id = user.id
    if tags:
        new_image.tags = image_tags
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return new_image
   

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


def rate_images_func(db: Session, order: str) -> list[ImageDB]:
    if order == "asc":
        return db.query(Image).order_by(Image.rate.asc()).all()
    else:
        return db.query(Image).order_by(Image.rate.desc()).all()


def get_transformation_func(db: Session, choice: int, image_id: int, user: User):
    db_image = db.query(Image).filter(Image.id == image_id,
                                     Image.user_id == user.id).first()
    def transform(num):
        if choice == 1:
            return [
                {'aspect_ratio': "1.0", 'gravity': "face",
                    'width': "0.7", 'crop': "thumb"},
                {'radius': "max"},
                {'color': "skyblue", 'effect': "outline"},
                {'color': "lightgray", 'effect': "shadow", 'x': 5, 'y': 8}
            ]
        elif choice == 2:
            return [
                {'aspect_ratio': "1.0", 'height': 250, 'crop': "fill"},
                {'border': "5px_solid_lightblue"}
            ]
        elif choice == 3:
            return [
                {'height': 400, 'width': 250, 'crop': "fill"},
                {'angle': 20},
                {'effect': "outline", 'color': "brown"},
                {'quality': "auto"},
                {'fetch_format': "auto"}
            ]
        else:
            raise HTTPException(
                status_code=400, detail="Wrong choice. Enter 1, 2 or 3.")

    transformation = transform(choice)
    pattern = r"/([^/]+)\.(png|jpg|jpeg|gif)$"
    match = re.search(pattern, db_image.url)
    id = match.group(1)
    transformed_image_url = CloudinaryImage(
        id).build_url(transformation=transformation)
    
    qr = generate_qr_code(transformed_image_url)
    db_image.url_view = transformed_image_url
    db_image.qr_code_view = qr
    db.commit()
    db.refresh(db_image)
    return db_image


def generate_qr_code(image_url):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(image_url)
    qr.make(fit=True)

    img = qr.make_image(image_factory=StyledPilImage,
                        module_drawer=RoundedModuleDrawer())

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    qr_code_url = cloudinary.uploader.upload(
        buffer, resource_type="image")["url"]

    return qr_code_url

