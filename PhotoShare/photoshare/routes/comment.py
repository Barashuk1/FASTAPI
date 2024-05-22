
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from photoshare.database.db import get_db
from photoshare.database.models import Comment, User
from photoshare.schemas import CommentCreate, CommentResponse as CommentSchema
from datetime import datetime
from photoshare.repository.comment import *
from photoshare.services.auth import auth_service


router = APIRouter(prefix='/images', tags=["comments"])


@router.post("/{image_id}/add_comment/", response_model=CommentSchema)
def create_comment(image_id: int, comment: CommentCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    return create_comment_func(image_id, comment, db, current_user)


@router.get("/{image_id}/comments/", response_model=List[CommentSchema])
def read_comments(photo_id: int, db: Session = Depends(get_db)):
    return read_comments_func(photo_id, db)


@router.put("/{image_id}/comments/{comment_id}/", response_model=CommentSchema)
def edit_comment(comment_id: int, comment_update: CommentCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    return edit_comment_func(comment_id, comment_update, db, current_user)


@router.delete("/{image_id}/comments/{comment_id}/")
def delete_comment(comment_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user_roles(["admin", "moderator"]))):
    return delete_comment_func(comment_id, db, current_user)
