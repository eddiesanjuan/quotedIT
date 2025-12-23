"""
Storage Service for Quoted (INFRA-001).

Provides unified file storage abstraction supporting:
- Local filesystem (development)
- S3-compatible storage (production)

All operations are async and handle errors gracefully.
"""

import os
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO, Union
from datetime import datetime

from ..config import settings
from .logging import get_logger

logger = get_logger("quoted.storage")

# S3 client (initialized lazily)
_s3_client = None
_s3_available = None


async def _get_s3_client():
    """Get S3 client, initializing if needed."""
    global _s3_client, _s3_available

    # Already determined S3 is not available
    if _s3_available is False:
        return None

    # Already have a working client
    if _s3_client is not None:
        return _s3_client

    # Check if S3 is configured
    if settings.storage_type != "s3" or not settings.s3_bucket:
        _s3_available = False
        logger.info("S3 not configured - using local storage")
        return None

    if not settings.aws_access_key or not settings.aws_secret_key:
        _s3_available = False
        logger.warning("S3 credentials missing - using local storage")
        return None

    # Try to connect
    try:
        import boto3
        from botocore.config import Config

        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "adaptive"},
            ),
        )
        # Test connection by checking bucket exists
        _s3_client.head_bucket(Bucket=settings.s3_bucket)
        _s3_available = True
        logger.info(f"S3 connected successfully to bucket: {settings.s3_bucket}")
        return _s3_client
    except ImportError:
        _s3_available = False
        logger.warning("boto3 package not installed - using local storage")
        return None
    except Exception as e:
        _s3_available = False
        logger.warning(f"S3 connection failed - using local storage: {e}")
        return None


class StorageService:
    """
    Unified storage service with S3 and local filesystem support.

    Automatically falls back to local storage when S3 is unavailable.
    """

    # Storage paths
    PDFS_PATH = "pdfs"
    UPLOADS_PATH = "uploads"
    LOGOS_PATH = "logos"

    def __init__(self):
        self.local_base = Path(settings.storage_path).parent  # ./data
        self._ensure_local_dirs()

    def _ensure_local_dirs(self):
        """Ensure local storage directories exist."""
        for subdir in [self.PDFS_PATH, self.UPLOADS_PATH, self.LOGOS_PATH]:
            path = self.local_base / subdir
            path.mkdir(parents=True, exist_ok=True)

    def _local_path(self, key: str) -> Path:
        """Get local filesystem path for a key."""
        return self.local_base / key

    def _s3_key(self, key: str) -> str:
        """Get S3 key (add environment prefix for isolation)."""
        return f"{settings.environment}/{key}"

    async def upload(
        self,
        key: str,
        data: Union[bytes, BinaryIO],
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload file to storage.

        Args:
            key: Storage path (e.g., "pdfs/quote-123.pdf")
            data: File content as bytes or file-like object
            content_type: MIME type for the file

        Returns:
            URL or path to access the file
        """
        s3 = await _get_s3_client()

        if s3:
            try:
                s3_key = self._s3_key(key)

                # Handle both bytes and file objects
                if isinstance(data, bytes):
                    s3.put_object(
                        Bucket=settings.s3_bucket,
                        Key=s3_key,
                        Body=data,
                        ContentType=content_type,
                    )
                else:
                    s3.upload_fileobj(
                        data,
                        settings.s3_bucket,
                        s3_key,
                        ExtraArgs={"ContentType": content_type},
                    )

                logger.debug(f"Uploaded to S3: {s3_key}")
                return f"s3://{settings.s3_bucket}/{s3_key}"
            except Exception as e:
                logger.error(f"S3 upload failed, falling back to local: {e}")
                # Fall through to local storage

        # Local storage fallback
        local_path = self._local_path(key)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(data, bytes):
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(data)
        else:
            # Read from file object and write
            content = data.read()
            async with aiofiles.open(local_path, "wb") as f:
                await f.write(content)

        logger.debug(f"Stored locally: {local_path}")
        return str(local_path)

    async def upload_file(
        self,
        key: str,
        file_path: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload a file from disk to storage.

        Args:
            key: Storage path (e.g., "pdfs/quote-123.pdf")
            file_path: Local path to the file to upload
            content_type: MIME type for the file

        Returns:
            URL or path to access the file
        """
        s3 = await _get_s3_client()

        if s3:
            try:
                s3_key = self._s3_key(key)
                s3.upload_file(
                    file_path,
                    settings.s3_bucket,
                    s3_key,
                    ExtraArgs={"ContentType": content_type},
                )
                logger.debug(f"Uploaded file to S3: {s3_key}")
                return f"s3://{settings.s3_bucket}/{s3_key}"
            except Exception as e:
                logger.error(f"S3 file upload failed, falling back to local: {e}")

        # For local storage, just return the existing path if key matches
        # or copy if different location needed
        local_path = self._local_path(key)
        if str(local_path) != file_path:
            import shutil
            local_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, local_path)

        return str(local_path)

    async def download(self, key: str) -> Optional[bytes]:
        """
        Download file from storage.

        Args:
            key: Storage path (e.g., "pdfs/quote-123.pdf")

        Returns:
            File content as bytes, or None if not found
        """
        s3 = await _get_s3_client()

        if s3 and key.startswith("s3://"):
            try:
                # Parse S3 URL
                s3_key = key.replace(f"s3://{settings.s3_bucket}/", "")
                response = s3.get_object(Bucket=settings.s3_bucket, Key=s3_key)
                return response["Body"].read()
            except Exception as e:
                logger.warning(f"S3 download failed: {e}")
                return None

        # Local storage
        local_path = self._local_path(key) if not key.startswith("/") else Path(key)
        if not local_path.exists():
            return None

        async with aiofiles.open(local_path, "rb") as f:
            return await f.read()

    async def delete(self, key: str) -> bool:
        """
        Delete file from storage.

        Args:
            key: Storage path (e.g., "pdfs/quote-123.pdf")

        Returns:
            True if deleted, False if not found or error
        """
        s3 = await _get_s3_client()

        if s3 and key.startswith("s3://"):
            try:
                s3_key = key.replace(f"s3://{settings.s3_bucket}/", "")
                s3.delete_object(Bucket=settings.s3_bucket, Key=s3_key)
                logger.debug(f"Deleted from S3: {s3_key}")
                return True
            except Exception as e:
                logger.warning(f"S3 delete failed: {e}")
                return False

        # Local storage
        local_path = self._local_path(key) if not key.startswith("/") else Path(key)
        if local_path.exists():
            local_path.unlink()
            logger.debug(f"Deleted locally: {local_path}")
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if file exists in storage."""
        s3 = await _get_s3_client()

        if s3 and key.startswith("s3://"):
            try:
                s3_key = key.replace(f"s3://{settings.s3_bucket}/", "")
                s3.head_object(Bucket=settings.s3_bucket, Key=s3_key)
                return True
            except Exception:
                return False

        # Local storage
        local_path = self._local_path(key) if not key.startswith("/") else Path(key)
        return local_path.exists()

    async def get_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get a public URL to access the file.

        For S3, generates a presigned URL.
        For local, returns the file path (caller must serve it).

        Args:
            key: Storage path
            expires_in: URL expiration time in seconds (S3 only)

        Returns:
            URL string or None if file doesn't exist
        """
        s3 = await _get_s3_client()

        if s3 and key.startswith("s3://"):
            try:
                s3_key = key.replace(f"s3://{settings.s3_bucket}/", "")
                url = s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": settings.s3_bucket, "Key": s3_key},
                    ExpiresIn=expires_in,
                )
                return url
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL: {e}")
                return None

        # Local storage - return path (endpoint must serve it)
        local_path = self._local_path(key) if not key.startswith("/") else Path(key)
        if local_path.exists():
            return str(local_path)
        return None

    async def health_check(self) -> dict:
        """Check storage health status."""
        result = {
            "local_available": True,
            "local_path": str(self.local_base),
        }

        s3 = await _get_s3_client()
        if s3:
            try:
                s3.head_bucket(Bucket=settings.s3_bucket)
                result["s3_available"] = True
                result["s3_bucket"] = settings.s3_bucket
            except Exception as e:
                result["s3_available"] = False
                result["s3_error"] = str(e)
        else:
            result["s3_available"] = False
            result["s3_configured"] = settings.storage_type == "s3"

        return result


# Singleton instance
storage_service = StorageService()
