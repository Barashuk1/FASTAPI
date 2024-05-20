
from fastapi import FastAPI, Depends,  APIRouter, HTTPException
from photoshare.schemas import *
from photoshare.database.db import Session
from photoshare.database.models import Comment

from photoshare.routes import *


def add_comment(db: Session, comment: CommentCreate, photo_id: int):
    db_comment = Comment(text=comment.text, photo_id=photo_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_photo(db: Session, photo_id: int):
    return db.query(Comment).filter(Comment.photo_id == photo_id).all()


def create_comment_func(image_id: int, comment: CommentCreate, db: Session):
    db_comment = Comment(text=comment.text, image_id=image_id, user_id=1)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def read_comments_func(photo_id: int, db: Session):
    comments = db.query(Comment).filter(Comment.image_id == photo_id).all()
    return comments


def edit_comment_func(photo_id: int, comment_id: int, comment_update: CommentCreate, db: Session):
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id, Comment.image_id == photo_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    db_comment.text = comment_update.text
    db_comment.updated_at = datetime.now()
    db.commit()
    db.refresh(db_comment)
    return db_comment


def delete_comment_func(photo_id: int, comment_id: int, db: Session, user: str):
    if user not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_comment = db.query(Comment).filter(
        Comment.id == comment_id, Comment.image_id == photo_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(db_comment)
    db.commit()
    return {"detail": "Comment deleted successfully"}




