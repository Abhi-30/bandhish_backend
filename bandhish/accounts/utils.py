import boto3
import uuid
from django.conf import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)


def upload_profile_image_to_s3(file_obj, user_id):
    extension = file_obj.name.split(".")[-1]
    key = f"user_profiles/{user_id}/{uuid.uuid4()}.{extension}"
    print(f"Uploading file to S3 with key: {key}")  # Debugging line
    s3_client.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={
            "ContentType": file_obj.content_type,
            "ACL": "private"
        }
    )

    return key


def generate_presigned_url(key, expires_in=3600):
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": key
        },
        ExpiresIn=expires_in
    )
