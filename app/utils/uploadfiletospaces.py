import boto3
from botocore.exceptions import NoCredentialsError

ACCESSKEY="DO00QQMECADE9G9GZY4D"
SecretKey="XhHsVcCRiUMzVXpNQwTin/+6Py6AN0FtiE17lYe4NQM"

def uploadfile():
    s3=boto3.client(
        's3',
        region_name='blr1',
        endpoint_url=f'https://profogapi-stage.blr1.digitaloceanspaces.com',
        aws_access_key_id=ACCESSKEY,
        aws_secret_access_key=SecretKey
    )
    return s3