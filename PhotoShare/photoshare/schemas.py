from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class TagModel(BaseModel):
    """
    Pydantic model representing tag data used for tag creation.

    :param name: The name of the tag (max length: 25).
    :type name: str
    """
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    """
    Pydantic model representing the response after tag creation.

    :param id: The unique identifier of the tag.
    :type id: int
    """
    id: int

    class Config:
        from_attributes = True


class ImageBase(BaseModel):
    """
    Pydantic model representing image data used for image creation.

    :param url: The URL of the image.
    :type url: str
    :param description: The description of the image.
    :type description: str
    :param created_at: The timestamp when the image was created.
    :type created_at: datetime
    """
    url: str
    description: str
    created_at: datetime


class ImageModel(ImageBase):
    """
    Pydantic model representing image data used for image creation.

    :param tags: The tags of the image (max length: 5).
    :type tags: Optional[str]
    """
    tags: Optional[str] = None

    class Config:
        max_tags = 5


class ImageDB(ImageBase):
    """
    Pydantic model representing image data retrieved from the database.

    :param id: The unique identifier of the image.
    :type id: int
    :param likes: The number of likes of the image.
    :type likes: int
    :param dislikes: The number of dislikes of the image.
    :type dislikes: int
    :param rate: The rating of the image.
    :type rate: float
    :param url_view: The URL of the image view.
    :type url_view: str
    :param qr_code_view: The QR code of the image view.
    :type qr_code_view: str
    :param tags: The tags of the image.
    :type tags: List[TagResponse]
    :param user_id: The unique identifier of the user who uploaded the image.
    :type user_id: int
    """
    id: int
    likes: int
    dislikes: int
    rate: float
    url_view: str | None
    qr_code_view: str | None
    tags: List[TagResponse]
    user_id: int


class ImageUpdate(ImageModel):
    """
    Pydantic model representing image data used for image update.

    :param description: The description of the image.
    :type description: str
    """
    description: str


class UserModel(BaseModel):
    """
    Pydantic model representing user data used for user creation.

    :param username: The username of the user (min length: 5, max length: 16).
    :type username: str
    :param email: The email address of the user.
    :type email: str
    :param password: The password of the user (min length: 6, max length: 10).
    :type password: str
    """
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    """
    Pydantic model representing user data retrieved from the database.

    :param id: The unique identifier of the user.
    :type id: int
    :param username: The username of the user.
    :type username: str
    :param email: The email address of the user.
    :type email: str
    :param created_at: The timestamp when the user was created.
    :type created_at: datetime
    :param role: The role of the user.
    :type role: str
    :param is_active: The status of the user.
    :type is_active: bool
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

    :param user: The user data.
    :type user: UserDb
    :param detail: The detail of the response.
    :type detail: str
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Pydantic model representing the token data.

    :param access_token: The access token.
    :type access_token: str
    :param refresh_token: The refresh token.
    :type refresh_token: str
    :param token_type: The token type.
    :type token_type: str
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    """
    Pydantic model representing the user profile data.

    :param id: The unique identifier of the user.
    :type id: int
    :param username: The username of the user.
    :type username: str
    :param email: The email address of the user.
    :type email: str
    :param created_at: The timestamp when the user was created.
    :type created_at: datetime
    :param images_count: The number of images uploaded by the user.
    :type images_count: int
    """
    id: int
    username: str
    email: str
    created_at: datetime
    images_count: int


class UserUpdate(BaseModel):
    """
    Pydantic model representing user data used for user update.

    :param username: The username of the user.
    :type username: Optional[str]
    :param email: The email address of the user.
    :type email: Optional[str]
    :param password: The password of the user.
    :type password: Optional[str]
    """
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class CommentBase(BaseModel):
    """
    Pydantic model representing comment data used for comment creation.

    :param text: The text of the comment.
    :type text: str
    """
    text: str


class CommentCreate(CommentBase):
    """
    Pydantic model representing comment data used for comment creation.
    """
    pass


class CommentResponse(CommentBase):
    """
    Pydantic model representing the response after comment creation.

    :param id: The unique identifier of the comment.
    :type id: int
    :param image_id: The unique identifier of the image.
    :type image_id: int
    :param created_at: The timestamp when the comment was created.
    :type created_at: datetime
    """
    id: int
    image_id: int
    created_at: datetime


class CommentSchema(BaseModel):
    """
    Pydantic model representing comment data retrieved from the database.

    :param image_id: The unique identifier of the image.
    :type image_id: int
    :param created_at: The timestamp when the comment was created.
    :type created_at: datetime
    :param text: The text of the comment.
    :type text: str
    """
    image_id: int
    created_at: datetime
    text: str


class ImageCreateFromPC(BaseModel):
    """
    Pydantic model representing image data used for image creation.

    :param description: The description of the image.
    :type description: str
    :param created_at: The timestamp when the image was created.
    :type created_at: datetime
    """
    description: str
    created_at: datetime
