"""S3 service for document storage and pre-signed URL generation."""
import uuid
import boto3
from botocore.exceptions import ClientError
from backend.config import AWS_REGION, S3_BUCKET, S3_PREFIX


def get_s3_client():
    """Create an S3 client."""
    return boto3.client("s3", region_name=AWS_REGION)


def ensure_bucket_exists():
    """Create the S3 bucket if it doesn't exist."""
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404' or error_code == 'NoSuchBucket':
            try:
                if AWS_REGION == 'us-east-1':
                    s3.create_bucket(Bucket=S3_BUCKET)
                else:
                    s3.create_bucket(
                        Bucket=S3_BUCKET,
                        CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                    )
            except ClientError:
                pass  # Bucket might already exist in another account


def upload_to_s3(file_content: bytes, filename: str, memory_id: str = None) -> str:
    """Upload a file to S3 and return the S3 key.

    Args:
        file_content: Raw file bytes
        filename: Original filename
        memory_id: Optional memory ID for folder organization

    Returns:
        S3 key (path within bucket)
    """
    s3 = get_s3_client()
    file_id = str(uuid.uuid4())[:8]

    # Organize: documents/{memory_id or 'unlinked'}/{file_id}_{filename}
    folder = memory_id or "unlinked"
    s3_key = f"{S3_PREFIX}{folder}/{file_id}_{filename}"

    try:
        ensure_bucket_exists()
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentDisposition=f'attachment; filename="{filename}"',
        )
        return s3_key
    except ClientError as e:
        print(f"[WARNING] S3 upload failed: {e}. Continuing without S3.")
        return None


def generate_presigned_url(s3_key: str, expiration: int = 3600) -> str:
    """Generate a pre-signed URL to download a file from S3.

    Args:
        s3_key: The S3 object key
        expiration: URL expiration time in seconds (default 1 hour)

    Returns:
        Pre-signed URL string, or None if generation fails
    """
    if not s3_key:
        return None

    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_key},
            ExpiresIn=expiration,
        )
        return url
    except ClientError:
        return None


def get_document_urls(documents: list) -> list:
    """Generate pre-signed URLs for a list of documents.

    Args:
        documents: List of document dicts with 's3_key' field

    Returns:
        Same list with 'download_url' field added
    """
    for doc in documents:
        s3_key = doc.get("s3_key")
        if s3_key:
            doc["download_url"] = generate_presigned_url(s3_key)
        else:
            doc["download_url"] = None
    return documents
