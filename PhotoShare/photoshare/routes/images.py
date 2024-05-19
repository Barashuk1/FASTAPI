from fastapi import FastAPI, Depends,  APIRouter
from photoshare.schemas import *
from photoshare.database.db import Session, get_db
from photoshare.repository.images import *
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request


router = APIRouter(prefix='/images', tags=["images"])
templates = Jinja2Templates(directory="photoshare/templates")


@router.post("/add")
def load_image(image: ImageCreate, db: Session = Depends(get_db)) -> ImageDB:
    return load_image_func(db, image)


@router.get("/url/{url_view}")
def get_image_url(url_view: str, db: Session = Depends(get_db)) -> ImageDB:
    return get_image_url_func(db, url_view)


@router.get('/rate/{action}')
def rate_images(request: Request, action: str, db: Session = Depends(get_db)):
    if action not in ['asc', 'desc']:
        return templates.TemplateResponse('404.html')
    rated_images = rate_images_func(db, action)
    return templates.TemplateResponse(
        'rate.html',
        {"request": request, "rated_images": rated_images, "action": action}
    )


@router.delete("/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)) -> ImageDB:
    return delete_image_func(db, image_id)


@router.put("/{image_id}")
def update_image(image_id: int, image: ImageUpdate, db: Session = Depends(get_db)) -> ImageDB:
    return update_image_func(db, image_id, image)


@router.get("/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)) -> ImageDB:
    return get_image_func(db, image_id)
