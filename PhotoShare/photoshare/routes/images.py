from fastapi import FastAPI, Depends,  APIRouter
from photoshare.schemas import ImageBase
from photoshare.database.db import Session, get_db
from photoshare.repository.images import *



router = APIRouter(prefix='/images', tags=["images"])


@router.post("/add")
def load_image(image: ImageBase, db: Session = Depends(get_db)):
    return load_image_func(db, image)


@router.delete("/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    return delete_image_func(db, image_id)
