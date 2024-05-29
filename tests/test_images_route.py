# import pytest
# from fastapi import HTTPException
# from sqlalchemy.orm import Session
# from unittest.mock import MagicMock, patch
# from datetime import datetime
# from photoshare.database.models import User
# from photoshare.schemas import *
# from photoshare.routes.images import *


# @pytest.fixture
# def mock_db_session():
#     session = MagicMock(spec=Session)
#     return session


# @pytest.fixture
# def mock_image_create():
#     image = ImageBase(description="This is a test image", tags=["test1", "test2"])
#     return image


# @pytest.fixture
# def mock_user():
#     user = User(id=1, username='testuser')
#     return user


# @patch("photoshare.routes.images.load_image_func")
# def test_load_image_func(mock_load_image_func):
#     tags = ["tag1", "tag2"]
#     image = ImageModel()  # Create a mock ImageModel object
#     expected_result = ImageDB()  # Create a mock ImageDB object as expected result

#     mock_load_image_func.return_value = expected_result

#     result = load_image(tags=tags, image=image, db=mock_db_session, current_user=mock_user)

#     assert result == expected_result
#     mock_load_image_func.assert_called_once_with(mock_db_session, image, tags, mock_user)

# # Test load_image_from_pc_func
# @patch("photoshare.routes.images.load_image_from_pc_func")
# def test_load_image_from_pc_func(mock_load_image_from_pc_func):
#     description = "Test description"
#     file_data = UploadFile(filename="test.jpg")  # Create a mock UploadFile object
#     tags = ["tag1", "tag2"]
#     expected_result = ImageDB()  # Create a mock ImageDB object as expected result

#     mock_load_image_from_pc_func.return_value = expected_result

#     result = load_image_from_pc(description=description, db=mock_db_session, file=file_data, current_user=mock_user, tags=tags)

#     assert result == expected_result
#     mock_load_image_from_pc_func.assert_called_once_with(mock_db_session, description, mock_user, file_data, tags)

# # Test get_image_url_func
# @patch("photoshare.routes.images.get_image_url_func")
# def test_get_image_url_func(mock_get_image_url_func):
#     url_view = "test_url"
#     expected_result = ImageDB()  # Create a mock ImageDB object as expected result

#     mock_get_image_url_func.return_value = expected_result

#     result = get_image_url(url_view=url_view, db=mock_db_session)

#     assert result == expected_result
#     mock_get_image_url_func.assert_called_once_with(mock_db_session, url_view)

# # Test rate_images_func
# @patch("photoshare.routes.images.rate_images_func")
# def test_rate_images_func(mock_rate_images_func):
#     order = "asc"
#     expected_result = []  # Define expected result, it could be a list of ImageDB objects

#     mock_rate_images_func.return_value = expected_result

#     result = rate_images(request=None, order=order, db=mock_db_session)

#     assert result == expected_result
#     mock_rate_images_func.assert_called_once_with(mock_db_session, order)

# # Test delete_image_func
# @patch("photoshare.routes.images.delete_image_func")
# def test_delete_image_func(mock_delete_image_func):
#     image_id = 1
#     expected_result = ImageDB()  # Create a mock ImageDB object as expected result

#     mock_delete_image_func.return_value = expected_result

#     result = delete_image(image_id=image_id, db=mock_db_session, current_user=mock_user)

#     assert result == expected_result
#     mock_delete_image_func.assert_called_once_with(mock_db_session, image_id, mock_user)

# # Test update_image_func
# @patch("photoshare.routes.images.update_image_func")
# def test_update_image_func(mock_update_image_func):
#     image_id = 1
#     image_update = ImageUpdate()  # Create a mock ImageUpdate object
#     expected_result = ImageDB()  # Create a mock ImageDB object as expected result

#     mock_update_image_func.return_value = expected_result

#     result = update_image(image_id=image_id, image=image_update, db=mock_db_session, current_user=mock_user)

#     assert result == expected_result
#     mock_update_image_func.assert_called_once_with(mock_db_session, image_id, image_update, mock_user)

# # Test get_image_func
# @patch("photoshare.routes.images.get_image_func")
# def test_get_image_func(mock_get_image_func):
#     image_id = 1
#     expected_result = ImageDB()  # Create a mock ImageDB object as expected result

#     mock_get_image_func.return_value = expected_result

#     result = get_image(image_id=image_id, db=mock_db_session)

#     assert result == expected_result
#     mock_get_image_func.assert_called_once_with(mock_db_session, image_id)

# # Test get_transformation_func
# @patch("photoshare.routes.images.get_transformation_func")
# def test_get_transformation_func(mock_get_transformation_func):
#     image_id = 1
#     choice = 1
#     expected_result = None  # Define expected result as needed

#     mock_get_transformation_func.return_value = expected_result

#     result = transform_image(image_id=image_id, choice=choice, db=mock_db_session, current_user=mock_user)

#     assert result == expected_result
#     mock_get_transformation_func.assert_called_once_with(mock_db_session, choice, image_id, mock_user)