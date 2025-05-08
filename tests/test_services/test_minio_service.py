from unittest.mock import AsyncMock, MagicMock

import pytest
from app.models.user_model import User
from minio.error import S3Error

pytestmark = pytest.mark.asyncio

async def test_upload_picture_sets_user_url(minio_service, db_session):
    user = User(id="123", email="user@example.com")
    
    file = MagicMock()
    file.filename = "sample.png"
    file.content_type = "image/png"
    file.read = AsyncMock(return_value=b"dummy image data")
    
    url = await minio_service.upload_profile_picture(user, file, db_session)
    
    assert user.profile_picture_url == url
    assert "sample.png" not in url  # should be a UUID name
    assert url.startswith("http://")
    assert url.endswith(".png")


async def test_bucket_created_if_missing(minio_service, db_session):
    from unittest.mock import AsyncMock, MagicMock

    user = User(id="123", email="user@example.com")
    file = MagicMock()
    file.filename = "image.png"
    file.content_type = "image/png"
    file.read = AsyncMock(return_value=b"image-bytes")

    db_session.commit = AsyncMock()

    minio_service.minio_client.bucket_exists.return_value = False
    minio_service.minio_client.make_bucket.reset_mock()

    await minio_service.upload_profile_picture(user, file, db_session)

    minio_service.minio_client.make_bucket.assert_called_once_with(minio_service.bucket_name)

async def test_no_bucket_creation_if_exists(minio_service, db_session):
    from unittest.mock import AsyncMock, MagicMock

    user = User(id="123", email="user@example.com")
    file = MagicMock()
    file.filename = "test.jpg"
    file.content_type = "image/jpeg"
    file.read = AsyncMock(return_value=b"bytes")

    db_session.commit = AsyncMock()

    minio_service.minio_client.bucket_exists.return_value = True
    minio_service.minio_client.make_bucket.reset_mock()

    await minio_service.upload_profile_picture(user, file, db_session)

    minio_service.minio_client.make_bucket.assert_not_called()

