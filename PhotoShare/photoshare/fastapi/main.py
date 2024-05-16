from fastapi import FastAPI, Depends
from schemas import ImageBase
from database.db import Session, get_db
from function import *

app = FastAPI()


@app.post("/image/add")
def load_image(image: ImageBase, db: Session = Depends(get_db)):
    return load_image_func(db, image)

@app.delete("/image/{image_id}")
def delete_image(image_id: int, db: Session = Depends(get_db)):
    return delete_image_func(db, image_id)