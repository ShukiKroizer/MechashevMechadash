import os
import sys
import boto3
from botocore.exceptions import BotoCoreError, ClientError

_bucket = os.environ.get('AWS_S3_BUCKET')
_region = os.environ.get('AWS_S3_REGION')

_aws_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
print(
    f"[s3] bucket={_bucket!r} region={_region!r} "
    f"key={'SET (' + _aws_key[:4] + '...)' if _aws_key else 'NOT SET'}",
    file=sys.stderr,
)

_s3 = boto3.client(
    's3',
    region_name=_region,
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
)


def upload_to_s3(file, filename):
    key = f"mechashev/{filename}"
    try:
        _s3.upload_fileobj(
            file,
            _bucket,
            key,
            ExtraArgs={'ContentType': file.content_type},
        )
        url = f"https://{_bucket}.s3.{_region}.amazonaws.com/{key}"
        print(f"[s3] uploaded OK → {url}", file=sys.stderr)
        return url
    except (BotoCoreError, ClientError) as e:
        print(f"[s3] upload FAILED: {e}", file=sys.stderr)
        raise RuntimeError(f"S3 upload failed: {e}") from e
