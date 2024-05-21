
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from photoshare.database.db import get_db
from photoshare.database.models import Comment, User
from photoshare.schemas import CommentCreate, Comment as CommentSchema
from datetime import datetime
from photoshare.repository.comment import *


router = APIRouter()


@router.post("/photos/{image_id}/comments/", response_model=CommentSchema)
def create_comment(image_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    return create_comment_func(image_id, comment, db)


@router.get("/photos/{photo_id}/comments/", response_model=List[CommentSchema])
def read_comments(photo_id: int, db: Session = Depends(get_db)):
    return read_comments_func(photo_id, db)




@router.put("/photos/{photo_id}/comments/{comment_id}/", response_model=CommentSchema)
def edit_comment(photo_id: int, comment_id: int, comment_update: CommentCreate, db: Session = Depends(get_db)):
    return edit_comment_func(photo_id, comment_id, comment_update, db)



@router.delete("/photos/{photo_id}/comments/{comment_id}/")
def delete_comment(photo_id: int, comment_id: int, db: Session = Depends(get_db), user: str = "admin"):
    return delete_comment_func(photo_id, comment_id, db, user)


