import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from photoshare_src.repository.images import *
from photoshare_src.database.models import Image, User, Tag, Comment
from photoshare_src.schemas import *
from fastapi import HTTPException
from io import BytesIO
from datetime import datetime, timezone


@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_user():
    user = User(id=1, username='testuser', role='user')
    return user


@pytest.fixture
def mock_admin_user():
    admin_user = User(id=1, username='adminuser', role='admin')
    return admin_user


@pytest.fixture
def mock_image_base():
    image = ImageBase(description="Тест", url="http://example.com/image.jpg", created_at="2023-01-01T00:00:00Z")
    return image

@pytest.fixture
def mock_image_update():
    image_update = ImageUpdate(
        description="update description", 
        url="http://example.com/updated_image.jpg", 
        created_at="2023-01-01T00:00:00Z",
        tags="good, nice")
    return image_update

@pytest.fixture
def mock_upload_file():
    file = MagicMock(spec=UploadFile)
    file.file = BytesIO(b"fake image data")
    return file


@pytest.fixture
def mock_tags():
    return ["tag1", "tag2"]


def test_load_image_func(mock_db_session, mock_image_base, mock_tags, mock_user):
    mock_tag = Tag(id=1, name="tag1")
    mock_db_session.query().filter().first.side_effect = [mock_tag, None]
    mock_db_session.commit.side_effect = None
    mock_db_session.refresh.side_effect = None

    result = load_image_func(mock_db_session, mock_image_base, mock_tags, mock_user)

    assert result.description == mock_image_base.description
    assert result.url == mock_image_base.url
    assert result.user_id == mock_user.id
    assert len(result.tags) == 2
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()
    mock_db_session.refresh.assert_called()


@patch("photoshare_src.repository.images.cloudinary.uploader.upload")
def test_load_image_from_pc_func(mock_upload, mock_db_session, mock_upload_file, mock_user, mock_tags):
    mock_upload.return_value = {"url": "http://example.com/uploaded_image.jpg"}
    mock_tag = Tag(id=1, name="tag1")
    mock_db_session.query().filter().first.side_effect = [mock_tag, None]
    mock_db_session.commit.side_effect = None
    mock_db_session.refresh.side_effect = None

    result = load_image_from_pc_func(mock_db_session, "Test description", mock_user, mock_upload_file, ",".join(mock_tags))

    assert result.url == "http://example.com/uploaded_image.jpg"
    assert result.description == "Test description"
    assert result.user_id == mock_user.id
    assert len(result.tags) == 2
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()
    mock_db_session.refresh.assert_called()


def test_delete_image_func_as_admin(mock_db_session, mock_admin_user):
    mock_image = Image(id=1, user_id=1)
    mock_db_session.query().filter().first.return_value = mock_image

    result = delete_image_func(mock_db_session, 1, mock_admin_user)

    assert result == mock_image
    mock_db_session.delete.assert_called_once_with(mock_image)
    mock_db_session.commit.assert_called()


def test_delete_image_func_as_non_admin(mock_db_session, mock_user):
    mock_image = Image(id=1, user_id=1)
    mock_db_session.query().filter().first.return_value = mock_image

    result = delete_image_func(mock_db_session, 1, mock_user)

    assert result == mock_image
    mock_db_session.delete.assert_called_once_with(mock_image)
    mock_db_session.commit.assert_called()


def test_delete_image_func_not_found(mock_db_session, mock_user):
    mock_db_session.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_image_func(mock_db_session, 1, mock_user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Image not found or you don't have permission to delete it."

# def test_update_image_func(mock_db_session, mock_image_update, mock_user):
#     mock_image = Image(
#         id=1,
#         url='http://example.com/old_image.jpg',
#         description='Old description',
#         tags=[Tag(id=1, name='bad'),],
#         comments=[Comment(id=1, text='Old comment')],
#         rate=4.5,
#         url_view='http://example.com/old_image_view.jpg',
#         qr_code_view='http://example.com/old_image_qr.jpg',       
#         created_at= datetime(2022, 1, 1, 0, 0, tzinfo=timezone.utc),
#         user_id=1,
#         user=mock_user
#     )
#     mock_db_session.query().filter().first.return_value = mock_image

#     result = update_image_func(mock_db_session, 1, mock_image_update, mock_user)

#     assert result.description == "update description"
#     assert result.url == 'http://example.com/updated_image.jpg'
#     assert result.created_at == datetime(2023, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    
#     assert result.tags == mock_image.tags
#     assert result.comments == mock_image.comments
#     mock_db_session.commit.assert_called_once()

def test_get_image_url_func(mock_db_session):
    mock_image = Image(id=1, url_view="http://example.com/image_view.jpg")
    mock_db_session.query().filter().first.return_value = mock_image

    result = get_image_url_func(mock_db_session, "http://example.com/image_view.jpg")

    assert result == mock_image


def test_get_image_func(mock_db_session):
    mock_image = Image(id=1)
    mock_db_session.query().filter().first.return_value = mock_image

    result = get_image_func(mock_db_session, 1)

    assert result == mock_image


def test_rate_images_func_asc(mock_db_session):
    mock_images = [
        Image(id=1, rate=1),
        Image(id=2, rate=2)
    ]
    mock_db_session.query().order_by().all.return_value = mock_images

    result = rate_images_func(mock_db_session, "asc")

    assert result == mock_images


def test_rate_images_func_desc(mock_db_session):
    mock_images = [
        Image(id=2, rate=2),
        Image(id=1, rate=1)
    ]
    mock_db_session.query().order_by().all.return_value = mock_images

    result = rate_images_func(mock_db_session, "desc")

    assert result == mock_images


@patch("photoshare_src.repository.images.CloudinaryImage")
def test_get_transformation_func(mock_cloudinary_image, mock_db_session, mock_user):
    mock_image = Image(id=1, url="http://example.com/image.jpg", user_id=1)
    mock_db_session.query().filter().first.return_value = mock_image

    mock_transformed_image_url = "http://example.com/transformed_image.jpg"
    mock_cloudinary_image.return_value.build_url.return_value = mock_transformed_image_url

    with patch("photoshare_src.repository.images.generate_qr_code", return_value="http://example.com/qr_code.jpg"):
        result = get_transformation_func(mock_db_session, 1, 1, mock_user)

    assert result.url_view == mock_transformed_image_url
    assert result.qr_code_view == "http://example.com/qr_code.jpg"
    mock_db_session.commit.assert_called()
    mock_db_session.refresh.assert_called_with(mock_image)


def test_generate_qr_code():
    image_url = "http://example.com/image.jpg"
    with patch("photoshare_src.repository.images.cloudinary.uploader.upload", return_value={"url": "http://example.com/qr_code.jpg"}) as mock_upload:
        result = generate_qr_code(image_url)
        assert result == "http://example.com/qr_code.jpg"
        mock_upload.assert_called()
