# minio_service.py
import io
import uuid
from minio import Minio
from settings.config import settings
from fastapi import UploadFile


class MinioService:
    def __init__(self):
        self.minio_client = Minio(
            settings.minio_host,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
        )
        self.bucket_name = settings.minio_bucket_name

    async def upload_profile_picture(self, file: UploadFile) -> str:
        extension = file.filename.split('.')[-1]
        fileName = f"{uuid.uuid4()}.{extension}"
        content = await file.read()

        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

        self.client.put_object(
            self.bucket_name,
            fileName,
            io.BytesIO(content),
            length=len(content),
            content_type=file.content_type
        )
        return f"{settings.minio_url}/{self.bucket_name}/{fileName}"