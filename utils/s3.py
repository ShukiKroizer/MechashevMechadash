import os
import boto3

_bucket = os.environ.get('AWS_S3_BUCKET')
_region = os.environ.get('AWS_S3_REGION')

_s3 = boto3.client(
    's3',
    region_name=_region,
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
)


def upload_to_s3(file, filename):
    key = f"mechashev/{filename}"
    _s3.upload_fileobj(
        file,
        _bucket,
        key,
        ExtraArgs={'ContentType': file.content_type, 'ACL': 'public-read'},
    )
    return f"https://{_bucket}.s3.{_region}.amazonaws.com/{key}"
