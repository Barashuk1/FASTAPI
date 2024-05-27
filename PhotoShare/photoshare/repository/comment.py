
from fastapi import FastAPI, Depends,  APIRouter, HTTPException
from photoshare.schemas import *
from photoshare.database.db import Session
from photoshare.database.models import Comment, User
from photoshare.routes import *


def get_comments_by_photo(db: Session, image_id: int) -> List[Comment]:
    """
    The get_comments_by_photo function returns all comments associated with a
    given photo.

    :param db: Pass in the database session
    :param image_id: Filter the comments by photo_id
    :return: A list of Comment objects
    """
    return db.query(Comment).filter(Comment.photo_id == image_id).all()


def create_comment_func(
    image_id: int,
    comment: CommentCreate,
    db: Session,
    user: User
) -> Comment:
    """
    The create_comment_func function creates a new comment in the database.

    :param image_id: Identify the image to which the comment is being added
    :param comment: Create a new comment
    :param db: Access the database
    :param user: Get the user_id of the comment creator
    :return: A Comment object
    """
    db_comment = Comment(text=comment.text, image_id=image_id)
    db_comment.user_id = user.id
    db_comment.created_at = datetime.now()
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def read_comments_func(image_id: int, db: Session) -> List[Comment]:
    """
    The read_comments_func function returns all comments for a given image_id.

    :param image_id: Specify the image id of the image we want to get comments for
    :param db: Pass the database session to the function
    :return: A list of comments
    """
    comments = db.query(Comment).filter(Comment.image_id == image_id).all()
    return comments


def edit_comment_func(
    comment_id: int,
    comment_update: CommentCreate,
    db: Session,
    user: User
) -> Comment:
    """
    The edit_comment_func function allows a user to edit their own comment.
    The function takes in the comment_id, which is the id of the comment that
    will be edited, and a CommentCreate object containing information about
    what text should replace the old text.

    :param comment_id: Identify the comment that is to be edited
    :param comment_update: Update the comment
    :param db: Access the database
    :param user: Get the user id from the database
    :return: The edited comment
    """
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


def delete_comment_func(
    comment_id: int,
    db: Session,
    user: User
) -> dict:
    """
    The delete_comment_func function deletes a comment from the database.

    :param comment_id: Specify the id of the comment to be deleted
    :param db: Access the database
    :param user: Check if the user has permission to delete a comment
    :raises HTTPException: If the user does not have permission to delete the comment
    :return: A dictionary ``{'detail': 'Comment deleted successfully'}`` if comment is deleted successfully
    """
    if user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="You don't have permission to delete it.")
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"detail": "Comment deleted successfully"}
