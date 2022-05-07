from settings import settings
from google.cloud import storage


def get_gcloud_signed_url(file_path):
    bucket_name = settings.GS_BUCKET_NAME
    creds = settings.GS_CREDENTIALS
    file_path = '' if file_path is None else file_path
    bucket = storage.Client().get_bucket(bucket_name)
    blob = bucket.blob(file_path)
    signed_url = blob.generate_signed_url(            
        expiration=2545367030, #epoch time            
        credentials=creds
    )
    return signed_url

