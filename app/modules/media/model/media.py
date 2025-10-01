import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlmodel import Field, Relationship, SQLModel


class MediaFile(SQLModel, table=True):
    """Media file model for storing file metadata"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # File information
    filename: str = Field(max_length=255, index=True)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)  # Path in storage
    file_url: str = Field(max_length=500)  # Public URL
    file_size: int = Field(description="File size in bytes")

    # Media type and format
    media_type: str = Field(
        max_length=50, index=True
    )  # "image", "video", "audio", "document"
    mime_type: str = Field(max_length=100)
    file_format: str = Field(max_length=10)  # "jpg", "png", "mp4", etc.

    # Dimensions (for images/videos)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    duration: Optional[float] = Field(default=None)  # For videos/audio in seconds

    # Processing status
    processing_status: str = Field(
        default="pending", max_length=20
    )  # "pending", "processing", "completed", "failed"

    # Quality and optimization
    quality: str = Field(
        default="original", max_length=20
    )  # "original", "compressed", "optimized"
    compression_level: Optional[int] = Field(default=None, ge=0, le=100)

    # Thumbnails and variants
    thumbnail_path: Optional[str] = Field(default=None, max_length=500)
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    variants: Optional[dict] = Field(
        default=None, sa_column=Column(JSON)
    )  # Different sizes/formats

    # User and ownership
    user_id: uuid.UUID = Field(index=True)
    is_public: bool = Field(default=True)
    is_deleted: bool = Field(default=False)

    # Usage tracking
    usage_count: int = Field(default=0)
    last_used_at: Optional[datetime] = Field(default=None)

    # Metadata
    metadata_: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(default=None)


class MediaProcessingJob(SQLModel, table=True):
    """Media processing job tracking"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Job information
    media_file_id: uuid.UUID = Field(foreign_key="mediafile.id", index=True)
    job_type: str = Field(max_length=50)  # "resize", "compress", "convert", "thumbnail"
    job_status: str = Field(
        default="queued", max_length=20
    )  # "queued", "processing", "completed", "failed"

    # Job parameters
    parameters: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Processing details
    priority: int = Field(default=1, ge=1, le=10)  # 1=lowest, 10=highest
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=500)

    # Queue management
    queue_name: str = Field(default="default", max_length=50)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MediaStorage(SQLModel, table=True):
    """Media storage configuration and usage tracking"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Storage configuration
    storage_type: str = Field(max_length=50)  # "local", "s3", "cloudinary", "cdn"
    bucket_name: Optional[str] = Field(default=None, max_length=100)
    region: Optional[str] = Field(default=None, max_length=50)
    endpoint_url: Optional[str] = Field(default=None, max_length=200)

    # Usage tracking
    total_files: int = Field(default=0)
    total_size_bytes: int = Field(default=0)
    monthly_usage_bytes: int = Field(default=0)

    # Limits and quotas
    max_file_size_bytes: Optional[int] = Field(default=None)
    max_total_size_bytes: Optional[int] = Field(default=None)
    allowed_formats: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))

    # Status
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)

    # Metadata
    config: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MediaAnalytics(SQLModel, table=True):
    """Media usage analytics"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Media reference
    media_file_id: uuid.UUID = Field(foreign_key="mediafile.id", index=True)

    # Usage metrics
    view_count: int = Field(default=0)
    download_count: int = Field(default=0)
    share_count: int = Field(default=0)

    # Performance metrics
    load_time_avg: float = Field(default=0.0)  # Average load time in seconds
    bandwidth_used: int = Field(default=0)  # Bytes served

    # Geographic data
    viewer_locations: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Device and platform data
    device_types: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    platforms: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Time tracking
    date_recorded: datetime = Field(default_factory=datetime.utcnow, index=True)
    week_start: datetime = Field(index=True)
    month_start: datetime = Field(index=True)
