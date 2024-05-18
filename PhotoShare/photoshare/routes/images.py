from fastapi import FastAPI, Depends,  APIRouter
from photoshare.schemas import *
from photoshare.database.db import Session, get_db
from photoshare.repository.images import *


router = APIRouter(prefix='/images', tags=["images"])


@router.post("/add")
def load_image(image: ImageBase, db: Session = Depends(get_db)):
    return load_image_func(db, image)


@router.get("/url")
def get_image_url(url_view: str, db: Session = Depends(get_db)):
    return get_image_url_func(db, url_view)


@router.delete("/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    return delete_image_func(db, image_id)


@router.put("/{image_id}")
def update_image(image_id: int, image: ImageUpdate, db: Session = Depends(get_db)):
    return update_image_func(db, image_id, image)


@router.get("/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    return get_image_func(db, image_id)