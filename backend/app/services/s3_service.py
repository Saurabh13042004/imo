"""S3 service for video uploads and management."""

import os
import boto3
from typing import Optional
from botocore.exceptions import ClientError
import uuid
from datetime import datetime


class S3Service:
    """Service for S3 operations."""

    def __init__(self):
        """Initialize S3 client."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'imo-s3-prod')

    def upload_video(self, file_content: bytes, file_name: str, user_id: str, product_id: str) -> Optional[str]:
        """
        Upload video to S3.
        
        Args:
            file_content: Video file bytes
            file_name: Original file name
            user_id: User ID
            product_id: Product ID
            
        Returns:
            S3 key if successful, None otherwise
        """
        try:
            # Generate unique key
            file_ext = file_name.split('.')[-1].lower()
            s3_key = f"user-reviews/{user_id}/{product_id}/{uuid.uuid4()}.{file_ext}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=f"video/{file_ext}",
                Metadata={
                    'user_id': user_id,
                    'product_id': product_id,
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'original_filename': file_name
                }
            )
            
            return s3_key
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return None

    def get_signed_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate signed URL for video.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Signed URL if successful, None otherwise
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating signed URL: {e}")
            return None

    def delete_video(self, s3_key: str) -> bool:
        """
        Delete video from S3.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False

    def list_user_videos(self, user_id: str, product_id: str) -> list:
        """
        List user's videos for a product.
        
        Args:
            user_id: User ID
            product_id: Product ID
            
        Returns:
            List of video keys
        """
        try:
            prefix = f"user-reviews/{user_id}/{product_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
        except ClientError as e:
            print(f"Error listing videos: {e}")
            return []
