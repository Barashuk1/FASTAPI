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
def load_image(tags: List[str], image: ImageModel, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)) -> ImageDB:
    if len(tags) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 tags allowed per image")
    return load_image_func(db, image, tags, current_user)


@router.post("/add_from_pc", response_model=ImageDB)
def load_image_from_pc(
    description: str,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(auth_service.get_current_user),
    tags: Optional[str] = None,) -> ImageDB: 
    return load_image_from_pc_func(db, description, current_user, file, tagsw)

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


@router.post("/{image_id}")
def transform_image(image_id: int, choice: int, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    return get_transformation_func(db, choice, image_id, current_user)
