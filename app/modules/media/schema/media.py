import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel


# Base schemas
class MediaFileBase(SQLModel):
    filename: str = Field(description="Generated filename")
    original_filename: str = Field(description="Original uploaded filename")
    file_path: str = Field(description="Storage path")
    file_url: str = Field(description="Public URL")
    file_size: int = Field(description="File size in bytes")
    media_type: str = Field(description="Media type: image, video, audio, document")
    mime_type: str = Field(description="MIME type")
    file_format: str = Field(description="File format/extension")
    width: Optional[int] = Field(default=None, description="Width for images/videos")
    height: Optional[int] = Field(default=None, description="Height for images/videos")
    duration: Optional[float] = Field(
        default=None, description="Duration for videos/audio"
    )
    processing_status: str = Field(default="pending", description="Processing status")
    quality: str = Field(default="original", description="Quality level")
    compression_level: Optional[int] = Field(
        default=None, description="Compression level 0-100"
    )
    thumbnail_path: Optional[str] = Field(
        default=None, description="Thumbnail storage path"
    )
    thumbnail_url: Optional[str] = Field(default=None, description="Thumbnail URL")
    user_id: str = Field(description="Owner user ID")
    is_public: bool = Field(default=True, description="Public visibility")
    usage_count: int = Field(default=0, description="Usage count")


class MediaProcessingJobBase(SQLModel):
    media_file_id: str = Field(description="Associated media file ID")
    job_type: str = Field(description="Job type: resize, compress, convert, thumbnail")
    job_status: str = Field(default="queued", description="Job status")
    parameters: Optional[Dict[str, Any]] = Field(
        default=None, description="Job parameters"
    )
    priority: int = Field(default=1, description="Job priority 1-10")
    queue_name: str = Field(default="default", description="Queue name")
    retry_count: int = Field(default=0, description="Current retry count")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class MediaStorageBase(SQLModel):
    storage_type: str = Field(description="Storage type: local, s3, cloudinary, cdn")
    bucket_name: Optional[str] = Field(
        default=None, description="Storage bucket/container name"
    )
    region: Optional[str] = Field(default=None, description="Storage region")
    endpoint_url: Optional[str] = Field(
        default=None, description="Storage endpoint URL"
    )
    total_files: int = Field(default=0, description="Total files stored")
    total_size_bytes: int = Field(default=0, description="Total storage used in bytes")
    monthly_usage_bytes: int = Field(default=0, description="Monthly usage in bytes")
    max_file_size_bytes: Optional[int] = Field(
        default=None, description="Maximum file size"
    )
    max_total_size_bytes: Optional[int] = Field(
        default=None, description="Maximum total storage"
    )
    is_active: bool = Field(default=True, description="Storage is active")
    is_default: bool = Field(default=False, description="Default storage")


class MediaAnalyticsBase(SQLModel):
    media_file_id: str = Field(description="Associated media file ID")
    view_count: int = Field(default=0, description="Number of views")
    download_count: int = Field(default=0, description="Number of downloads")
    share_count: int = Field(default=0, description="Number of shares")
    load_time_avg: float = Field(
        default=0.0, description="Average load time in seconds"
    )
    bandwidth_used: int = Field(default=0, description="Bandwidth used in bytes")


# Public schemas
class MediaFilePublic(MediaFileBase):
    id: str
    variants: Optional[Dict[str, Any]] = None
    metadata_: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None


class MediaProcessingJobPublic(MediaProcessingJobBase):
    id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MediaStoragePublic(MediaStorageBase):
    id: str
    allowed_formats: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class MediaAnalyticsPublic(MediaAnalyticsBase):
    id: str
    viewer_locations: Optional[Dict[str, Any]] = None
    device_types: Optional[Dict[str, Any]] = None
    platforms: Optional[Dict[str, Any]] = None
    date_recorded: datetime
    week_start: datetime
    month_start: datetime


# Create schemas
class MediaFileCreate(BaseModel):
    file: bytes = Field(description="File content as bytes")
    filename: str = Field(description="Original filename")
    media_type: str = Field(description="Media type")
    is_public: bool = Field(default=True, description="Public visibility")
    tags: Optional[List[str]] = Field(default=None, description="File tags")


class MediaProcessingJobCreate(MediaProcessingJobBase):
    pass


class MediaStorageCreate(MediaStorageBase):
    pass


class MediaAnalyticsCreate(MediaAnalyticsBase):
    pass


# Update schemas
class MediaFileUpdate(BaseModel):
    filename: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata_: Optional[Dict[str, Any]] = None


class MediaProcessingJobUpdate(BaseModel):
    job_status: Optional[str] = None
    priority: Optional[int] = None
    error_message: Optional[str] = None


class MediaStorageUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    max_file_size_bytes: Optional[int] = None
    max_total_size_bytes: Optional[int] = None
    allowed_formats: Optional[List[str]] = None


class MediaAnalyticsUpdate(BaseModel):
    view_count: Optional[int] = None
    download_count: Optional[int] = None
    share_count: Optional[int] = None
    load_time_avg: Optional[float] = None
    bandwidth_used: Optional[int] = None


# Response schemas
class MediaFileList(BaseModel):
    data: List[MediaFilePublic]
    total: int
    user_id: Optional[str] = None
    media_type: Optional[str] = None


class MediaProcessingJobList(BaseModel):
    data: List[MediaProcessingJobPublic]
    total: int
    status: Optional[str] = None


class MediaStorageList(BaseModel):
    data: List[MediaStoragePublic]
    total: int


class MediaAnalyticsList(BaseModel):
    data: List[MediaAnalyticsPublic]
    total: int
    media_file_id: Optional[str] = None


# Upload response
class MediaUploadResponse(BaseModel):
    media_file: MediaFilePublic
    upload_url: Optional[str] = None
    processing_jobs: List[str] = Field(default_factory=list)


# Processing request schemas
class ProcessingJobCreate(BaseModel):
    media_file_id: str
    job_type: str
    parameters: Optional[Dict[str, Any]] = None
    priority: int = 1


class ProcessingJobUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[float] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ImageResizeRequest(BaseModel):
    width: int = Field(..., gt=0, description="Target width in pixels")
    height: int = Field(..., gt=0, description="Target height in pixels")
    maintain_aspect_ratio: bool = True


class ImageCropRequest(BaseModel):
    x: int = Field(..., ge=0, description="X coordinate of crop start")
    y: int = Field(..., ge=0, description="Y coordinate of crop start")
    width: int = Field(..., gt=0, description="Crop width")
    height: int = Field(..., gt=0, description="Crop height")


class VideoCompressRequest(BaseModel):
    target_bitrate: Optional[str] = Field(
        None, description="Target bitrate (e.g., '2M', '5M')"
    )
    target_resolution: Optional[str] = Field(
        None, description="Target resolution (e.g., '1920x1080', '1280x720')"
    )
    preset: str = Field(
        "medium",
        description="Compression preset: ultrafast, fast, medium, slow, veryslow",
    )


class VideoTrimRequest(BaseModel):
    start_time: float = Field(..., ge=0, description="Start time in seconds")
    end_time: float = Field(..., gt=0, description="End time in seconds")


# Storage configuration
class StorageConfig(BaseModel):
    type: str = Field(description="Storage type")
    bucket: Optional[str] = None
    region: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
