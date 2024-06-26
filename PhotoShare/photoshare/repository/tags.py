from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from photoshare.database.models import Tag
from photoshare.schemas import TagModel, TagResponse


async def get_tags(
    skip: int,
    limit: int,
    db: Session
) -> List[Tag]:
    """
    Function to get tags from the database

    :param skip: offset
    :param limit: limit
    :param db: SQLAlchemy session
    :return: list of tags
    """
    return db.query(Tag).offset(skip).limit(limit).all()


async def get_tag(
    tag_id: int,
    db: Session
) -> Tag:
    """
    Function to get tag by id from the database

    :param tag_id: tag id
    :param db: SQLAlchemy session
    :return: Tag object
    """
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def create_tag(
    body: TagModel,
    db: Session
) -> Tag:
    """
    Function to create tag in the database

    :param body: TagModel object
    :param db: SQLAlchemy session
    :return: Tag object
    """
    if db.query(Tag).filter(Tag.name == body.name).first():
        raise HTTPException(status_code=400, detail="Tag already created")
#!!!!!!!!
    tag = Tag(name=body.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def update_tag(
    tag_id: int,
    body: TagModel,
    db: Session
) -> Tag | None:
    """
    Function to update tag in the database

    :param tag_id: tag id
    :param body: TagModel object
    :param db: SQLAlchemy session
    :return: Tag object or None
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        #!!!!!!!!
        tag.name = body.name
        db.commit()
    return tag


async def remove_tag(
    tag_id: int,
    db: Session
)  -> Tag | None:
    """
    Function to remove tag from the database

    :param tag_id: tag id
    :param db: SQLAlchemy session
    :return: Tag object or None
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag
