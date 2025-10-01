import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional

from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.modules.media.crud.media_crud import (
    crud_media_analytics,
    crud_media_file,
    crud_media_processing_job,
    crud_media_storage,
)
from app.modules.media.model.media import MediaFile, MediaProcessingJob, MediaStorage
from app.modules.media.schema.media import (
    ImageCropRequest,
    ImageResizeRequest,
    MediaAnalyticsCreate,
    MediaAnalyticsList,
    MediaAnalyticsPublic,
    MediaFileCreate,
    MediaFileList,
    MediaFilePublic,
    MediaFileUpdate,
    MediaProcessingJobCreate,
    MediaProcessingJobList,
    MediaProcessingJobPublic,
    MediaStorageCreate,
    MediaStorageList,
    MediaStoragePublic,
    MediaUploadResponse,
    ProcessingJobCreate,
    ProcessingJobUpdate,
    VideoCompressRequest,
    VideoTrimRequest,
)


class MediaFileService:
    """Service layer for media file operations."""

    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_VIDEO_TYPES = ["video/mp4", "video/avi", "video/mov", "video/quicktime"]
    ALLOWED_AUDIO_TYPES = ["audio/mp3", "audio/wav", "audio/m4a"]
    ALLOWED_DOCUMENT_TYPES = ["application/pdf", "text/plain", "application/msword"]

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    @staticmethod
    def validate_file(file: UploadFile) -> str:
        """Validate uploaded file and return media type."""
        if file.size and file.size > MediaFileService.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")

        content_type = file.content_type or ""

        if content_type in MediaFileService.ALLOWED_IMAGE_TYPES:
            return "image"
        elif content_type in MediaFileService.ALLOWED_VIDEO_TYPES:
            return "video"
        elif content_type in MediaFileService.ALLOWED_AUDIO_TYPES:
            return "audio"
        elif content_type in MediaFileService.ALLOWED_DOCUMENT_TYPES:
            return "document"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

    @staticmethod
    def generate_filename(original_filename: str) -> str:
        """Generate a unique filename."""
        extension = Path(original_filename).suffix
        return f"{uuid.uuid4()}{extension}"

    @staticmethod
    async def upload_file(
        session: Session, file: UploadFile, user_id: str, storage_path: str = "uploads"
    ) -> MediaUploadResponse:
        """Upload and store a media file."""
        # Validate file
        media_type = MediaFileService.validate_file(file)

        # Generate filename
        original_filename = file.filename or "unnamed_file"
        filename = MediaFileService.generate_filename(original_filename)

        # Read file content
        content = await file.read()

        # Get storage configuration
        storage = crud_media_storage.get_default_storage(session)
        if not storage:
            # Create default local storage if none exists
            storage = crud_media_storage.create(
                session, obj_in=MediaStorage(storage_type="local", is_default=True)
            )

        # Save file locally (for now)
        file_path = f"{storage_path}/{filename}"
        os.makedirs(storage_path, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(content)

        # Create media file record
        media_file = crud_media_file.create(
            session,
            obj_in=MediaFile(
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                file_url=f"/media/{filename}",  # Public URL
                file_size=len(content),
                media_type=media_type,
                mime_type=file.content_type or "application/octet-stream",
                file_format=Path(filename).suffix[1:],
                user_id=user_id,
                processing_status="completed",  # For now, mark as completed
            ),
        )

        # Create processing jobs if needed
        processing_jobs = []
        if media_type == "image":
            # Create thumbnail job
            job = crud_media_processing_job.create(
                session,
                obj_in=MediaProcessingJob(
                    media_file_id=media_file.id,
                    job_type="thumbnail",
                    parameters={"size": "300x300"},
                ),
            )
            processing_jobs.append(job.id)

        elif media_type == "video":
            # Create thumbnail and compression jobs
            thumbnail_job = crud_media_processing_job.create(
                session,
                obj_in=MediaProcessingJob(
                    media_file_id=media_file.id,
                    job_type="thumbnail",
                    parameters={"time": "00:00:01"},
                ),
            )
            processing_jobs.append(thumbnail_job.id)

        return MediaUploadResponse(
            media_file=MediaFilePublic.model_validate(media_file),
            processing_jobs=processing_jobs,
        )

    @staticmethod
    def get_user_media(
        session: Session,
        user_id: str,
        media_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> MediaFileList:
        """Get user's media files."""
        files = crud_media_file.get_user_files(
            session, user_id=user_id, media_type=media_type, skip=skip, limit=limit
        )

        return MediaFileList(
            data=[MediaFilePublic.model_validate(f) for f in files],
            total=len(files),
            user_id=user_id,
            media_type=media_type,
        )

    @staticmethod
    def get_public_media(
        session: Session,
        media_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> MediaFileList:
        """Get public media files."""
        files = crud_media_file.get_public_files(
            session, media_type=media_type, skip=skip, limit=limit
        )

        return MediaFileList(
            data=[MediaFilePublic.model_validate(f) for f in files],
            total=len(files),
            media_type=media_type,
        )

    @staticmethod
    def get_media_file(session: Session, file_id: str) -> Optional[MediaFile]:
        """Get a media file by ID."""
        return crud_media_file.get(session, id=file_id)

    @staticmethod
    def update_media_file(
        session: Session, file_id: str, updates: MediaFileUpdate
    ) -> Optional[MediaFile]:
        """Update media file metadata."""
        db_obj = crud_media_file.get(session, id=file_id)
        if db_obj:
            return crud_media_file.update(
                session, db_obj=db_obj, obj_in=updates.model_dump(exclude_unset=True)
            )
        return None

    @staticmethod
    def delete_media_file(session: Session, file_id: str, user_id: str) -> bool:
        """Delete a media file (soft delete)."""
        media_file = crud_media_file.get(session, id=file_id)
        if media_file and media_file.user_id == user_id:
            crud_media_file.soft_delete(session, file_id)
            return True
        return False

    @staticmethod
    def get_storage_stats(session: Session, user_id: str) -> Dict[str, Any]:
        """Get storage statistics for a user."""
        return crud_media_file.get_storage_stats(session, user_id)


class MediaProcessingService:
    """Service layer for media processing operations."""

    @staticmethod
    def get_pending_jobs(
        session: Session, queue_name: str = "default", limit: int = 10
    ) -> MediaProcessingJobList:
        """Get pending processing jobs."""
        jobs = crud_media_processing_job.get_pending_jobs(
            session, queue_name=queue_name, limit=limit
        )

        return MediaProcessingJobList(
            data=[MediaProcessingJobPublic.model_validate(j) for j in jobs],
            total=len(jobs),
            status="queued",
        )

    @staticmethod
    def get_jobs_for_media_file(
        session: Session, media_file_id: str
    ) -> MediaProcessingJobList:
        """Get all processing jobs for a media file."""
        jobs = crud_media_processing_job.get_jobs_by_media_file(session, media_file_id)

        return MediaProcessingJobList(
            data=[MediaProcessingJobPublic.model_validate(j) for j in jobs],
            total=len(jobs),
        )

    @staticmethod
    def update_job_status(
        session: Session, job_id: str, status: str, error_message: Optional[str] = None
    ) -> Optional[MediaProcessingJob]:
        """Update processing job status."""
        return crud_media_processing_job.update_job_status(
            session, job_id, status, error_message
        )

    @staticmethod
    def create_processing_job(
        session: Session,
        media_file_id: str,
        job_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 1,
    ) -> MediaProcessingJob:
        """Create a new processing job."""
        return crud_media_processing_job.create(
            session,
            obj_in=MediaProcessingJob(
                media_file_id=media_file_id,
                job_type=job_type,
                parameters=parameters or {},
                priority=priority,
            ),
        )

    @staticmethod
    def process_image(
        session: Session,
        request,  # : ImageProcessingRequest - commented out due to schema changes
    ) -> List[MediaProcessingJob]:
        """Process image with various operations."""
        jobs = []

        for operation in request.operations:
            job = MediaProcessingService.create_processing_job(
                session,
                request.media_file_id,
                "image_process",
                {"operation": operation, "output_formats": request.output_formats},
            )
            jobs.append(job)

        session.commit()
        return jobs

    @staticmethod
    def process_video(
        session: Session,
        request,  # : VideoProcessingRequest - commented out due to schema changes
    ) -> List[MediaProcessingJob]:
        """Process video with various operations."""
        jobs = []

        for operation in request.operations:
            job = MediaProcessingService.create_processing_job(
                session,
                request.media_file_id,
                "video_process",
                {"operation": operation, "output_formats": request.output_formats},
            )
            jobs.append(job)

        session.commit()
        return jobs


class MediaStorageService:
    """Service layer for media storage operations."""

    @staticmethod
    def get_storages(session: Session) -> MediaStorageList:
        """Get all storage configurations."""
        storages = crud_media_storage.get_active_storages(session)

        return MediaStorageList(
            data=[MediaStoragePublic.model_validate(s) for s in storages],
            total=len(storages),
        )

    @staticmethod
    def get_default_storage(session: Session) -> Optional[MediaStorage]:
        """Get default storage configuration."""
        return crud_media_storage.get_default_storage(session)

    @staticmethod
    def create_storage(
        session: Session, storage_data: MediaStorageCreate
    ) -> MediaStorage:
        """Create a new storage configuration."""
        storage_obj = MediaStorage(**storage_data.model_dump())
        return crud_media_storage.create(session, obj_in=storage_obj)

    @staticmethod
    def update_storage_usage(
        session: Session, storage_id: str, files_added: int = 0, size_added: int = 0
    ) -> Optional[MediaStorage]:
        """Update storage usage statistics."""
        return crud_media_storage.update_usage(
            session, storage_id, files_added, size_added
        )


class MediaAnalyticsService:
    """Service layer for media analytics operations."""

    @staticmethod
    def get_media_analytics(
        session: Session,
        media_file_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> MediaAnalyticsList:
        """Get analytics for a media file."""
        analytics = crud_media_analytics.get_analytics_for_media(
            session, media_file_id, start_date, end_date
        )

        return MediaAnalyticsList(
            data=[MediaAnalyticsPublic.model_validate(a) for a in analytics],
            total=len(analytics),
            media_file_id=media_file_id,
        )

    @staticmethod
    def track_media_usage(
        session: Session,
        media_file_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track media usage (view, download, share)."""
        metrics = {}

        if action == "view":
            metrics["view_count"] = 1
        elif action == "download":
            metrics["download_count"] = 1
        elif action == "share":
            metrics["share_count"] = 1

        if metadata:
            if "load_time" in metadata:
                metrics["load_time_avg"] = metadata["load_time"]
            if "bandwidth" in metadata:
                metrics["bandwidth_used"] = metadata["bandwidth"]

        crud_media_analytics.update_analytics(session, media_file_id, metrics)

        # Update usage count in media file
        crud_media_file.update_usage_count(session, media_file_id)


# Service instances
media_file_service = MediaFileService()
media_processing_service = MediaProcessingService()
media_storage_service = MediaStorageService()
media_analytics_service = MediaAnalyticsService()
