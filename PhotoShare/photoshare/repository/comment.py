
from fastapi import FastAPI, Depends,  APIRouter, HTTPException
from photoshare.schemas import *
from photoshare.database.db import Session
from photoshare.database.models import Comment, User
from photoshare.routes import *


def get_comments_by_photo(db: Session, photo_id: int):
    return db.query(Comment).filter(Comment.image_id == photo_id).all()


def create_comment_func(image_id: int, comment: CommentCreate, db: Session, user: User):
    db_comment = Comment(text=comment.text, image_id=image_id)
    db_comment.user_id = user.id
    db_comment.created_at = datetime.now()
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def read_comments_func(photo_id: int, db: Session):
    comments = db.query(Comment).filter(Comment.image_id == photo_id).all()
    return comments


def edit_comment_func(comment_id: int, comment_update: CommentCreate, db: Session, user: User):
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id, Comment.user_id == user.id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment:
        db_comment.text = comment_update.text
        db_comment.updated_at = datetime.now()
        db.commit()
        db.refresh(db_comment)
    return db_comment


def delete_comment_func(comment_id: int, db: Session, user: User):
    if user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="You don't have permission to delete it.")
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"detail": "Comment deleted successfully"}




