from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from photoshare.database.models import Tag
from photoshare.schemas import TagModel


async def get_tags(skip: int, limit: int, db: Session) -> List[Tag]:
    return db.query(Tag).offset(skip).limit(limit).all()


async def get_tag(tag_id: int, db: Session) -> Tag:
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def create_tag(body: TagModel, db: Session) -> Tag:
    if db.query(Tag).filter(Tag.name == body.name).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    tag = Tag(name=body.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


async def update_tag(tag_id: int, body: TagModel, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        tag.name = body.name
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session)  -> Tag | None:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag

#tag with autorization

# from typing import List

# from sqlalchemy.orm import Session
# from sqlalchemy import and_

# from photoshare.database.models import Tag, User
# from photoshare.schemas import TagModel


# async def get_tags(skip: int, limit: int, user: User, db: Session) -> List[Tag]:
#     return db.query(Tag).filter(Tag.user_id == user.id).offset(skip).limit(limit).all()


# async def get_tag(tag_id: int, user: User, db: Session) -> Tag:
#     return db.query(Tag).filter(and_(Tag.id == tag_id, Tag.user_id == user.id)).first()


# async def create_tag(body: TagModel, user: User, db: Session) -> Tag:
#     tag = Tag(name=body.name, user_id=user.id)
#     db.add(tag)
#     db.commit()
#     db.refresh(tag)
#     return tag


# async def update_tag(tag_id: int, body: TagModel, user: User, db: Session) -> Tag | None:
#     tag = db.query(Tag).filter(and_(Tag.id == tag_id, Tag.user_id == user.id)).first()
#     if tag:
#         tag .name = body.name
#         db.commit()
#     return tag


# async def remove_tag(tag_id: int, user: User, db: Session) -> Tag | None:
#     tag = db.query(Tag).filter(and_(Tag.id == tag_id, Tag.user_id == user.id)).first()
#     if tag:
#         db.delete(tag)
#         db.commit()
#     return tag
