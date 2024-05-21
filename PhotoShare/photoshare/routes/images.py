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
templates = Jinja2Templates(directory="photoshare/templates")


@router.post("/add")
def load_image(image: ImageBase, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)) -> ImageDB:
    return load_image_func(db, image, current_user)


@router.get("/url/{url_view}")
def get_image_url(url_view: str, db: Session = Depends(get_db)) -> ImageDB:
    return get_image_url_func(db, url_view)


@router.get('/rate')
def rate_images(request: Request, order: str = 'asc', db: Session = Depends(get_db)):
    rated_images= rate_images_func(db, order)
    return templates.TemplateResponse(
        'rate.html',
        {"request": request, "rated_images": rated_images, "order": order}
    )


@router.delete("/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)) -> ImageDB:
    return delete_image_func(db, image_id, current_user)


@router.put("/{image_id}")
def update_image(image_id: int, image: ImageUpdate, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)) -> ImageDB:
    return update_image_func(db, image_id, image, current_user)


@router.get("/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)) -> ImageDB:
    return get_image_func(db, image_id)
