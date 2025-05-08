# minio_service.py
from http.client import HTTPException
import io
import logging
import uuid
from minio import Minio
from settings.config import settings
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User

logger = logging.getLogger(__name__)

class MinioService:
    def __init__(self):
        self.minio_client = Minio(
            settings.minio_host,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False
        )
        self.bucket_name = settings.minio_bucket_name

    async def upload_profile_picture(self, user:User,  file: UploadFile, session: AsyncSession) -> str:
        extension = file.filename.split('.')[-1]
        fileName = f"{uuid.uuid4()}.{extension}"
        content = await file.read()
    
        if not self.minio_client.bucket_exists(self.bucket_name):
            logger.info(f"Creating bucket: {self.bucket_name}")
            self.minio_client.make_bucket(self.bucket_name)

        self.minio_client.put_object(
            self.bucket_name,
            fileName,
            io.BytesIO(content),
            length=len(content),
            content_type=file.content_type
        )
        logger.info(f"Uploaded the image to minio server")
        profile_picture_url =f"{settings.minio_url}/{self.bucket_name}/{fileName}"
        user.profile_picture_url = profile_picture_url
        await session.commit()
        return profile_picture_url