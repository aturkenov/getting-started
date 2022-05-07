import uuid
import aiohttp
from fastapi import UploadFile
from gcloud.aio.storage import Storage
from settings import settings


class GCloudStorage:

    EXPIRATION: int = settings.URL_EXPIRATION_TIME
    BUCKET_NAME: str = settings.GS_BUCKET_NAME
    STORAGE = Storage(service_file=settings.GOOGLE_APPLICATION_CREDENTIALS_PATH)

    async def save(
        self,
        file: UploadFile,
        folder: str,
    ) -> str:
        file_extension: str = file.filename.split('.')[-1]
        file_name: str = str(uuid.uuid4()) + '.' + file_extension

        full_file_name: str = folder + file_name

        async with aiohttp.ClientSession(timeout=settings.UPLOAD_TIMEOUT) as session:
            client = Storage(session=session, service_file=settings.GOOGLE_APPLICATION_CREDENTIALS_PATH)

            file_data: bytes = await file.read()
            await client.upload(
                bucket=self.BUCKET_NAME,
                object_name=full_file_name,
                file_data=file_data,
            )

        return full_file_name

    async def get_signed_url(
        self,
        file_name: str,
    ) -> str:
        file_path = '' if not file_name else file_name
        bucket = self.STORAGE.get_bucket(self.BUCKET_NAME)
        try:
            blob = await bucket.get_blob(file_path)
        except Exception as e:
            blob = bucket.new_blob(file_path)

        return await blob.get_signed_url(
            expiration=self.EXPIRATION,
        )


gcloud_storage: GCloudStorage = GCloudStorage()
