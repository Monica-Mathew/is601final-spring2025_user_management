from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.user_model import User, UserRole
from app.services.user_service import UserService
from app.utils.nickname_gen import generate_nickname

async def test_upload_picture_returns_user_url(minio_service,email_service, db_session):
    user_data = {
        "nickname": generate_nickname(),
        "email": "valid_user@example.com",
        "password": "ValidPassword123!",
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
        "email": "valid_user@example.com",
        "password": "ValidPassword123!",
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