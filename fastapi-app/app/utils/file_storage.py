"""
File storage utility supporting local filesystem and S3.
"""
import os
import base64
import uuid
from pathlib import Path
from typing import Optional, BinaryIO, Tuple
from datetime import datetime

try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

from app.core.config import settings


class FileStorage:
    """File storage handler supporting local and S3 storage."""
    
    def __init__(self):
        self.storage_type = os.getenv("FILESYSTEM_DISK", "local").lower()
        self.local_storage_path = Path(os.getenv("FILESYSTEM_LOCAL_PATH", "./storage/uploads"))
        self.s3_bucket = os.getenv("FILESYSTEM_S3_BUCKET", "")
        self.s3_region = os.getenv("FILESYSTEM_S3_REGION", "us-east-1")
        self.s3_access_key = os.getenv("FILESYSTEM_S3_ACCESS_KEY", "")
        self.s3_secret_key = os.getenv("FILESYSTEM_S3_SECRET_KEY", "")
        
        # Ensure local storage directory exists
        if self.storage_type == "local":
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client if using S3
        if self.storage_type == "s3" and S3_AVAILABLE:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.s3_access_key,
                aws_secret_access_key=self.s3_secret_key,
                region_name=self.s3_region
            )
        else:
            self.s3_client = None
    
    def _generate_file_path(self, filename: str, folder: Optional[str] = None) -> str:
        """Generate a unique file path."""
        # Create date-based folder structure
        date_folder = datetime.now().strftime("%Y/%m/%d")
        file_uuid = str(uuid.uuid4())
        file_ext = Path(filename).suffix if filename else ""
        new_filename = f"{file_uuid}{file_ext}"
        
        if folder:
            return f"{folder}/{date_folder}/{new_filename}"
        return f"{date_folder}/{new_filename}"
    
    def save_file(
        self,
        file_content: bytes,
        filename: str,
        folder: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Save file to storage.
        Returns: (storage_path, disk_type)
        """
        storage_path = self._generate_file_path(filename, folder)
        
        if self.storage_type == "s3" and self.s3_client:
            return self._save_to_s3(file_content, storage_path, content_type)
        else:
            return self._save_to_local(file_content, storage_path)
    
    def _save_to_local(self, file_content: bytes, storage_path: str) -> Tuple[str, str]:
        """Save file to local filesystem."""
        full_path = self.local_storage_path / storage_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(file_content)
        
        return str(storage_path), "local"
    
    def _save_to_s3(self, file_content: bytes, storage_path: str, content_type: Optional[str] = None) -> Tuple[str, str]:
        """Save file to S3."""
        if not self.s3_client:
            raise ValueError("S3 client not initialized")
        
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=storage_path,
                Body=file_content,
                **extra_args
            )
            return storage_path, "s3"
        except ClientError as e:
            raise ValueError(f"Failed to upload to S3: {str(e)}")
    
    def get_file(self, storage_path: str, disk: Optional[str] = None) -> bytes:
        """Retrieve file from storage."""
        disk_type = disk or self.storage_type
        
        if disk_type == "s3" and self.s3_client:
            return self._get_from_s3(storage_path)
        else:
            return self._get_from_local(storage_path)
    
    def _get_from_local(self, storage_path: str) -> bytes:
        """Retrieve file from local filesystem."""
        full_path = self.local_storage_path / storage_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {storage_path}")
        
        with open(full_path, "rb") as f:
            return f.read()
    
    def _get_from_s3(self, storage_path: str) -> bytes:
        """Retrieve file from S3."""
        if not self.s3_client:
            raise ValueError("S3 client not initialized")
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=storage_path
            )
            return response['Body'].read()
        except ClientError as e:
            raise FileNotFoundError(f"File not found in S3: {str(e)}")
    
    def delete_file(self, storage_path: str, disk: Optional[str] = None) -> bool:
        """Delete file from storage."""
        disk_type = disk or self.storage_type
        
        if disk_type == "s3" and self.s3_client:
            return self._delete_from_s3(storage_path)
        else:
            return self._delete_from_local(storage_path)
    
    def _delete_from_local(self, storage_path: str) -> bool:
        """Delete file from local filesystem."""
        full_path = self.local_storage_path / storage_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    def _delete_from_s3(self, storage_path: str) -> bool:
        """Delete file from S3."""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.s3_bucket,
                Key=storage_path
            )
            return True
        except ClientError:
            return False
    
    def get_file_url(self, storage_path: str, disk: Optional[str] = None) -> str:
        """Get public URL for file."""
        disk_type = disk or self.storage_type
        
        if disk_type == "s3" and self.s3_client:
            return f"https://{self.s3_bucket}.s3.{self.s3_region}.amazonaws.com/{storage_path}"
        else:
            # For local storage, return a relative URL
            base_url = os.getenv("APP_URL", "http://localhost:9001")
            return f"{base_url}/files/{storage_path}"


# Global file storage instance
file_storage = FileStorage()

