
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from photoshare.database.db import get_db
from photoshare.database.models import Comment, User
from photoshare.schemas import CommentCreate, Comment as CommentSchema
from datetime import datetime
from photoshare.repository.comment import *

router = APIRouter(prefix='/comments', tags=["comments"])



@router.post("/{image_id}", response_model=CommentSchema)
def create_comment(image_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    return create_comment_func(image_id, comment, db)


@router.get("/{image_id}", response_model=List[CommentSchema])
def read_comments(image_id: int, db: Session = Depends(get_db)):
    return read_comments_func(image_id, db)


@router.put("/{image_id}/{comment_id}", response_model=CommentSchema)
def edit_comment(image_id: int, comment_id: int, comment_update: CommentCreate, db: Session = Depends(get_db)):
    return edit_comment_func(image_id, comment_id, comment_update, db)



@router.delete("/{image_id}/{comment_id}/")
def delete_comment(image_id: int, comment_id: int, db: Session = Depends(get_db), user: str = "admin"):
    return delete_comment_func(image_id, comment_id, db, user)


