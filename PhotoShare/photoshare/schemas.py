from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True

class ImageBase(BaseModel):
    url: str
    description: str
    created_at: datetime

class ImageModel(ImageBase):
    tags: List[int]

class ImageDB(ImageBase):
    id: int
    likes: int
    dislikes: int
    rate: float
    url_view: str | None
    qr_code_view: str | None
    tags: List[TagResponse]
    user_id: int


class ImageUpdate(ImageModel):
    description: str


class UserModel(BaseModel):
    """
    Pydantic model representing user data used for user creation.

    Attributes:
    - username (str): The username of the user (min length: 5, max length: 16).
    - email (str): The email address of the user.
    - password (str): The password of the user (min length: 6, max length: 10).
    """
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    """
    Pydantic model representing user data retrieved from the database.

    Attributes:
    - id (int): The unique identifier of the user.
    - username (str): The username of the user.
    - email (str): The email address of the user.
    - created_at (datetime): The timestamp when the user was created.
    """
    id: int
    username: str
    email: str
    created_at: datetime
    role: str
    is_active: bool
    class ConfigDict:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Pydantic model representing the response after user creation.

    Attributes:
    - user (UserDb): The user data.
    - detail (str): Additional detail message (default: "User successfully created").
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Pydantic model representing the token response.

    Attributes:
    - access_token (str): The access token.
    - refresh_token (str): The refresh token.
    - token_type (str): The type of token (default: "bearer").
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    images_count: int

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    image_id: int
    created_at: datetime


class CommentSchema(BaseModel):
    image_id: int
    created_at: datetime
    text: str
