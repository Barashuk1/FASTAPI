from photoshare.database.db import Session
from photoshare.database.models import Image, User, Tag
from photoshare.schemas import *
from photoshare.conf.config import settings
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
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)


def load_image_func(
    db: Session,
    image: ImageBase,
    tags: List[str],
    user: User
) -> ImageDB:
    """
    Function to load image to the database

    :param db: SQLAlchemy session
    :param image: ImageBase object
    :param tags: list of tags
    :param user: User object
    :return: ImageDB object
    """
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


def load_image_from_pc_func(
    db: Session,
    description: str,
    user: User,
    file: UploadFile = File(),
    tags: Optional[str] = None
) -> ImageDB:
    """
    Function to load image from PC to the database

    :param db: SQLAlchemy session
    :param description: description of the image
    :param user: User object
    :param file: UploadFile object
    :param tags: list of tags
    :raise HTTPException: if tags have uncorrect format
    :return: ImageDB object
    """
    upload_result = cloudinary.uploader.upload(
        file.file,
        overwrite=True
    )
    if tags:
        try:
            tags_list = [tag.strip() for tag in tags.split(",")]
            image_tags = []
            for tag_name in tags_list:
                # Перевіряємо, чи існує тег з такою назвою
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    # Якщо тега не існує, створюємо новий
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)
                image_tags.append(tag)
        except:
            raise HTTPException(
                status_code=400, detail="Uncorrect fromat of tags"
            )

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


def delete_image_func(
    db: Session,
    image_id: int,
    user: User
) -> ImageDB:
    """
    Function to delete image from the database

    :param db: SQLAlchemy session
    :param image_id: id of the image
    :param user: User object
    :raise HTTPException: if image not found or user doesn't have permission to delete it
    :return: ImageDB object
    """
    if user.role == "admin":
        db_image = db.query(Image).filter(Image.id == image_id).first()
    else:
        db_image = db.query(Image).filter(
            Image.id == image_id, Image.user_id == user.id
        ).first()
        if not db_image:
            # Якщо зображення не знайдено або не належить поточному користувачу, викинути виняток HTTP 404
            raise HTTPException(
                status_code=404,
                detail="Image not found or you don't have permission to delete it."
            )
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image


def update_image_func(
    db: Session,
    image_id: int,
    image: ImageUpdate,
    user: User
) -> ImageDB:
    """
    Function to update image in the database

    :param db: SQLAlchemy session
    :param image_id: id of the image
    :param image: ImageUpdate object
    :param user: User object
    :raise HTTPException: if image not found or user doesn't have permission to update it
    :return: ImageDB object
    """
    if user.role == "admin":
        db_image = db.query(Image).filter(Image.id == image_id).first()
    else:
        db_image = db.query(Image).filter(
            Image.id == image_id, Image.user_id == user.id
        ).first()
        if not db_image:
            # Якщо зображення не знайдено або не належить поточному користувачу, викинути виняток HTTP 404
            raise HTTPException(
                status_code=404,
                detail="Image not found or you don't have permission to delete it."
            )
    if db_image:
        for key, val in image.model_dump().items():
            setattr(db_image, key, val)
        db.commit()
        db.refresh(db_image)
    return db_image


def get_image_url_func(
    db: Session,
    url: str
) -> ImageDB:
    """
    Function to get image by url_view

    :param db: SQLAlchemy session
    :param url_view: url_view of the image
    :return: ImageDB object
    """
    db_image = db.query(Image).filter(Image.url == url).first()
    return db_image


def get_image_func(
    db: Session,
    image_id: int
) -> ImageDB:
    """
    Function to get image by id

    :param db: SQLAlchemy session
    :param image_id: id of the image
    :return: ImageDB object
    """
    db_image = db.query(Image).filter(Image.id == image_id).first()
    return db_image


def rate_images_func(
    db: Session,
    order: str
) -> list[ImageDB]:
    """
    Function to get images sorted by rate

    :param db: SQLAlchemy session
    :param order: order of sorting
    :return: list of ImageDB objects
    """
    if order == "asc":
        return db.query(Image).order_by(Image.rate.asc()).all()
    else:
        return db.query(Image).order_by(Image.rate.desc()).all()


def get_transformation_func(
    db: Session,
    choice: int,
    image_id: int,
    user: User
) -> ImageDB:
    """
    Function to get transformation of the image

    :param db: SQLAlchemy session
    :param choice: choice of transformation
    :param image_id: id of the image
    :param user: User object
    :return: ImageDB object
    """
    db_image = db.query(Image).filter(
        Image.id == image_id, Image.user_id == user.id
    ).first()
    def transform(num: int) -> list[dict[str, str | int]]:
        """
        Function to choose transformation

        :param num: number of transformation
        :raise HTTPException: if choice is wrong
        :return: list of transformations
        """
        if choice == 1:
            return [
                {
                    'aspect_ratio': "1.0", 'gravity': "face",
                    'width': "0.7", 'crop': "thumb"
                },
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
    transformed_image_url = CloudinaryImage(id).build_url(
        transformation=transformation
    )

    qr = generate_qr_code(transformed_image_url)
    db_image.url_view = transformed_image_url
    db_image.qr_code_view = qr
    db.commit()
    db.refresh(db_image)
    return db_image


def generate_qr_code(image_url: str) -> str:
    """
    Function to generate QR code

    :param image_url: url of the image
    :return: url of the QR code
    """
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(image_url)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer()
    )

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    qr_code_url = cloudinary.uploader.upload(
        buffer, resource_type="image"
    )["url"]

    return qr_code_url


def search_images_by_description_func(
    db: Session,
    description: str
) -> list[ImageDB]:
    """
    Function to search images by description

    :param db: SQLAlchemy session
    :param description: description of the image
    :return: list of ImageDB objects
    """
    return db.query(Image).filter(
        Image.description.ilike(f"%{description}%")
    ).all()


def search_images_by_tags_func(
    db: Session,
    tags: list[str]
) -> list[ImageDB]:
    """
    Function to search images by tags

    :param db: SQLAlchemy session
    :param tags: list of tags
    :return: list of ImageDB objects
    """
    return list(set(db.query(Image).join(Image.tags).filter(
        Tag.name.in_(tags)
    ).all()))


def search_images_by_user_func(
    db: Session,
    username: str
) -> list[ImageDB]:
    """
    Function to search images by user

    :param db: SQLAlchemy session
    :param username: username of the user
    :raise HTTPException: if user doesn't have permission to this type of search
    :return: list of ImageDB objects
    """
    user = db.query(User).filter(User.username == username).first()
    if user.role == 'user':
        raise HTTPException(
            status_code=400,
            detail="You don't have permission to this type of search"
        )
    return db.query(Image).filter(Image.user_id == user.id).all()
