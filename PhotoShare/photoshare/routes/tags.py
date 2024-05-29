from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from photoshare.database.db import get_db
from photoshare.schemas import TagModel, TagResponse
from photoshare.repository import tags as repository_tags
from photoshare.services.auth import auth_service
from photoshare.database.models import User

router = APIRouter(prefix='/tags', tags=["tags"])


@router.get("/", response_model=List[TagResponse])
async def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all tags

    :param skip: The number of tags to skip
    :param limit: The number of tags to return
    :param db: Database session
    :return: List of tags
    """
    tags = await repository_tags.get_tags(skip, limit, db)
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
async def read_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a tag by ID

    :param tag_id: The ID of the tag to retrieve
    :param db: Database session
    :return: The tag
    """
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagResponse)
async def create_tag(
    body: TagModel,
    db: Session = Depends(get_db)
):
    """
    Create a new tag

    :param body: The tag data
    :param db: Database session
    :return: The created tag
    """
    return await repository_tags.create_tag(body, db)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    body: TagModel,
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Update a tag

    :param body: The updated tag data
    :param tag_id: The ID of the tag to update
    :param db: Database session
    :raise HTTPException: If the tag is not found
    :return: The updated tag
    """
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.delete("/{tag_id}", response_model=TagResponse)
async def remove_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove a tag

    :param tag_id: The ID of the tag to remove
    :param db: Database session
    :raise HTTPException: If the tag is not found
    :return: The removed tag
    """
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag
