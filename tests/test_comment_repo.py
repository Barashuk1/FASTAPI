import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from photoshare_src.repository.comment import *
from photoshare_src.database.models import Comment, User
from photoshare_src.schemas import *


@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_user():
    user = User(id=1, username='testuser')
    return user


@pytest.fixture
def mock_comment_create():
    comment = CommentCreate(text="This is a test comment")
    return comment


@pytest.fixture
def mock_comment_update():
    comment_update = CommentCreate(text="Updated comment text")
    return comment_update


def test_get_comments_by_photo(mock_db_session):
    comments = [
        Comment(id=1, text="Nice photo!", created_at=None,
                updated_at=None, image_id=1, user_id=1),
        Comment(id=2, text="Amazing shot!", created_at=None,
                updated_at=None, image_id=1, user_id=1)
    ]

    mock_db_session.query().filter().all.return_value = comments

    result = get_comments_by_photo(mock_db_session, image_id=1)

    assert len(result) == 2
    assert result[0].text == "Nice photo!"
    assert result[1].text == "Amazing shot!"


def test_create_comment_func(mock_db_session, mock_comment_create, mock_user):
    result = create_comment_func(
        image_id=1,
        comment=mock_comment_create,
        db=mock_db_session,
        user=mock_user
    )

    mock_db_session.add.assert_called_once()
    added_comment = mock_db_session.add.call_args[0][0]

    assert added_comment.text == mock_comment_create.text
    assert added_comment.image_id == 1
    assert added_comment.user_id == mock_user.id

    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(added_comment)

    assert result == added_comment


def test_read_comments_func(mock_db_session):
    comments = [
        Comment(id=1, text="Nice photo!", created_at=None,
                updated_at=None, image_id=1, user_id=1),
        Comment(id=2, text="Amazing shot!", created_at=None,
                updated_at=None, image_id=1, user_id=1)
    ]

    mock_db_session.query().filter().all.return_value = comments

    result = read_comments_func(image_id=1, db=mock_db_session)

    assert len(result) == 2
    assert result[0].text == "Nice photo!"
    assert result[1].text == "Amazing shot!"


def test_edit_existing_comment(mock_db_session, mock_user):
    comment_id = 1
    comment_update = CommentCreate(text="Updated text")
    existing_comment = Comment(
        id=comment_id, user_id=mock_user.id, text="Old text")
    mock_db_session.query().filter().first.return_value = existing_comment

    edited_comment = edit_comment_func(
        comment_id, comment_update, mock_db_session, mock_user)

    assert edited_comment.text == comment_update.text
    assert isinstance(edited_comment.updated_at, datetime)
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called_once_with(existing_comment)


def test_edit_non_existing_comment(mock_db_session, mock_user):
    comment_id = 1
    comment_update = CommentCreate(text="Updated text")
    mock_db_session.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        edit_comment_func(comment_id, comment_update,
                          mock_db_session, mock_user)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Comment not found"


def test_delete_comment_as_admin(mock_db_session, mock_user):
    comment_id = 1
    admin_user = User(id=1, role="admin")
    existing_comment = Comment(id=comment_id)
    mock_db_session.query().filter().first.return_value = existing_comment

    result = delete_comment_func(comment_id, mock_db_session, admin_user)

    assert result == {"detail": "Comment deleted successfully"}
    assert mock_db_session.delete.called
    assert mock_db_session.commit.called


def test_delete_comment_as_non_admin(mock_db_session, mock_user):
    comment_id = 1
    non_admin_user = User(id=2, role="user")
    existing_comment = Comment(id=comment_id)
    mock_db_session.query().filter().first.return_value = existing_comment

    with pytest.raises(HTTPException) as exc_info:
        delete_comment_func(comment_id, mock_db_session, non_admin_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You don't have permission to delete it."


def test_delete_non_existing_comment(mock_db_session, mock_user):
    comment_id = 1
    non_existing_comment_id = 2
    mock_db_session.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        delete_comment_func(non_existing_comment_id,
                            mock_db_session, mock_user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You don't have permission to delete it."
