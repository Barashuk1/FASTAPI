from fastapi import FastAPI, Depends,  APIRouter
from photoshare.schemas import *
from photoshare.database.db import Session, get_db
from photoshare.repository.images import *
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from photoshare.database.models import User
from photoshare.services.auth import auth_service

router = APIRouter(prefix='/images', tags=["images"])
templates = Jinja2Templates(directory="photoshare/services/templates")


@router.post("/add")
def load_image(
    tags: List[str],
    image: ImageModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
) -> ImageDB:
    """
    Load an image to the database

    :param tags: The tags to be associated with the image
    :param image: The image data
    :param db: Database session
    :param current_user: The user uploading the image
    :raise HTTPException: If more than 5 tags are provided
    :return: The created image
    """
    if len(tags) > 5:
        raise HTTPException(
            status_code=400, detail="Maximum 5 tags allowed per image"
        )
    return load_image_func(db, image, tags, current_user)


@router.post("/add_from_pc", response_model=ImageDB)
def load_image_from_pc(
    description: str,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(auth_service.get_current_user),
    tags: Optional[str] = None
) -> ImageDB:
    """
    Load an image to the database from a file on the local machine

    :param description: The description of the image
    :param db: Database session
    :param file: The image file
    :param current_user: The user uploading the image
    :param tags: The tags to be associated with the image
    :return: The created image
    """
    return load_image_from_pc_func(db, description, current_user, file, tags)

@router.get("/url/{url_view}")
def get_image_url(
    url_view: str,
    db: Session = Depends(get_db)
) -> ImageDB:
    """
    Get an image by its URL

    :param url_view: The URL of the image
    :param db: Database session
    :return: The image
    """
    return get_image_url_func(db, url_view)


@router.get('/rate')
def rate_images(
    request: Request,
    order: str = 'asc',
    db: Session = Depends(get_db)
):
    """
    Rate images

    :param request: The request
    :param order: The order to display the images in
    :param db: Database session
    :return: The rated images
    """
    rated_images= rate_images_func(db, order)
    return templates.TemplateResponse(
        'rate.html',
        {"request": request, "rated_images": rated_images, "order": order}
    )


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
) -> ImageDB:
    """
    Delete an image

    :param image_id: The id of the image to delete
    :param db: Database session
    :param current_user: The user deleting the image
    :return: The deleted image
    """
    return delete_image_func(db, image_id, current_user)


@router.put("/{image_id}")
def update_image(
    image_id: int,
    image: ImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
) -> ImageDB:
    """
    Update an image

    :param image_id: The id of the image to update
    :param image: The updated image
    :param db: Database session
    :param current_user: The user updating the image
    :return: The updated image
    """
    return update_image_func(db, image_id, image, current_user)


@router.get("/{image_id}")
def get_image(
    image_id: int,
    db: Session = Depends(get_db)
) -> ImageDB:
    """
    Get an image by its ID

    :param image_id: The id of the image
    :param db: Database session
    :return: The image
    """
    return get_image_func(db, image_id)


@router.post("/{image_id}")
def transform_image(
    image_id: int,
    choice: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Transform an image

    :param image_id: The id of the image to transform
    :param choice: The transformation to apply
    :param db: Database session
    :param current_user: The user transforming the image
    :return: The transformed image
    """
    return get_transformation_func(db, choice, image_id, current_user)
