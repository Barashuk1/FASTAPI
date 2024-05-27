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
def create_comment(
    image_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Create a new comment on an image

    :param image_id: The id of the image to comment on
    :param comment: The comment to be created
    :param db: Database session
    :param current_user: The user creating the comment
    :return: The created comment
    """
    return create_comment_func(image_id, comment, db, current_user)


@router.get("/{image_id}/comments/", response_model=List[CommentSchema])
def read_comments(
    photo_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all comments on an image

    :param photo_id: The id of the image to get comments for
    :param db: Database session
    :return: List of comments
    """
    return read_comments_func(photo_id, db)


@router.put("/{image_id}/comments/{comment_id}/", response_model=CommentSchema)
def edit_comment(
    comment_id: int,
    comment_update: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Edit a comment on an image

    :param comment_id: The id of the comment to edit
    :param comment_update: The updated comment
    :param db: Database session
    :param current_user: The user editing the comment
    :return: The edited comment
    """
    return edit_comment_func(comment_id, comment_update, db, current_user)


@router.delete("/{image_id}/comments/{comment_id}/")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        auth_service.get_current_user_roles(["admin", "moderator"])
    )
):
    """
    Delete a comment on an image

    :param comment_id: The id of the comment to delete
    :param db: Database session
    :param current_user: The user deleting the comment
    :return: The deleted comment
    """
    return delete_comment_func(comment_id, db, current_user)
