from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.user_model import User, UserRole
from app.services.user_service import UserService
from app.utils.nickname_gen import generate_nickname

async def test_upload_picture_returns_user_url(minio_service,email_service, db_session):
    user_data = {
        "nickname": generate_nickname(),
        "email": "valid_user12@example.com",
        "password": "ValidPassword123!",
        "role": UserRole.AUTHENTICATED.name
    }
    user = await UserService.create(db_session, user_data, email_service)
    file = MagicMock()
    file.filename = "sample.png"
    file.content_type = "image/png"
    file.read = AsyncMock(return_value=b"dummy image data")

    url = await minio_service.upload_profile_picture(user, file, db_session)

    assert "sample.png" not in url  # should be a UUID name
    assert url.startswith("http://")
    assert url.endswith(".png")


async def test_no_bucket_creation_if_exists(minio_service,email_service, db_session):
    from unittest.mock import AsyncMock, MagicMock

    user_data = {
        "nickname": generate_nickname(),
        "email": "valid_user23@example.com",
        "password": "ValidPassword123!",
        "role": UserRole.AUTHENTICATED.name
    }
    user = await UserService.create(db_session, user_data, email_service)
    file = MagicMock()
    file.filename = "test.jpg"
    file.content_type = "image/jpeg"
    file.read = AsyncMock(return_value=b"bytes")

    minio_service.minio_client.bucket_exists.return_value = True
    minio_service.minio_client.make_bucket.reset_mock()

    await minio_service.upload_profile_picture(user, file, db_session)

    minio_service.minio_client.make_bucket.assert_not_called()

async def test_uploaded_file_url_format_and_user_update(db_session, email_service,minio_service):
    user_data = {
        "nickname": generate_nickname(),
        "email": "valid_user45@example.com",
        "password": "ValidPassword123!",
        "role": UserRole.ADMIN.name
    }
    user = await UserService.create(db_session, user_data, email_service)
    assert user is not None
    assert user.email == user_data["email"]
    file = MagicMock()
    file.filename = "avatar.jpeg"
    file.content_type = "image/jpeg"
    file.read = AsyncMock(return_value=b"data")

    url = await minio_service.upload_profile_picture(user, file, db_session)

    assert url.startswith("http://")
    assert url.endswith(".png")
    assert user.profile_picture_url == url ## user update
