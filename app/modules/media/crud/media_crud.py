from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Session, desc, select

from app.modules.media.model.media import (
    MediaAnalytics,
    MediaFile,
    MediaProcessingJob,
    MediaStorage,
)
from app.shared.crud.base import CRUDBase


class CRUDMediaFile(CRUDBase[MediaFile, MediaFile, MediaFile]):
    def get(self, session: Session, id: str) -> Optional[MediaFile]:
        """Get media file by string ID."""
        return session.get(MediaFile, id)

    def get_by_filename(self, session: Session, filename: str) -> Optional[MediaFile]:
        """Get media file by filename."""
        return session.exec(
            select(MediaFile).where(MediaFile.filename == filename)
        ).first()

    def get_user_files(
        self,
        session: Session,
        user_id: str,
        media_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[MediaFile]:
        """Get media files for a user."""
        query = select(MediaFile).where(
            MediaFile.user_id == user_id, MediaFile.is_deleted == False
        )

        if media_type:
            query = query.where(MediaFile.media_type == media_type)

        return list(
            session.exec(
                query.order_by(desc(MediaFile.created_at)).offset(skip).limit(limit)
            )
        )

    def get_public_files(
        self,
        session: Session,
        media_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[MediaFile]:
        """Get public media files."""
        query = select(MediaFile).where(
            MediaFile.is_public == True, MediaFile.is_deleted == False
        )

        if media_type:
            query = query.where(MediaFile.media_type == media_type)

        return list(
            session.exec(
                query.order_by(desc(MediaFile.created_at)).offset(skip).limit(limit)
            )
        )

    def update_usage_count(
        self, session: Session, media_file_id: str
    ) -> Optional[MediaFile]:
        """Increment usage count for a media file."""
        media_file = session.get(MediaFile, media_file_id)
        if media_file:
            media_file.usage_count += 1
            media_file.last_used_at = datetime.utcnow()
            session.add(media_file)
            session.commit()
            session.refresh(media_file)
        return media_file

    def soft_delete(self, session: Session, media_file_id: str) -> Optional[MediaFile]:
        """Soft delete a media file."""
        media_file = session.get(MediaFile, media_file_id)
        if media_file:
            media_file.is_deleted = True
            session.add(media_file)
            session.commit()
            session.refresh(media_file)
        return media_file

    def get_storage_stats(self, session: Session, user_id: str) -> Dict[str, Any]:
        """Get storage statistics for a user."""
        # Get user's files
        files = list(
            session.exec(
                select(MediaFile).where(
                    MediaFile.user_id == user_id, MediaFile.is_deleted == False
                )
            )
        )

        total_files = len(files)
        total_size = sum(f.file_size for f in files)

        # Count by type
        type_counts = {}
        type_sizes = {}
        for file in files:
            media_type = file.media_type
            type_counts[media_type] = type_counts.get(media_type, 0) + 1
            type_sizes[media_type] = type_sizes.get(media_type, 0) + file.file_size

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "files_by_type": [
                {
                    "type": media_type,
                    "count": count,
                    "size_bytes": type_sizes[media_type],
                }
                for media_type, count in type_counts.items()
            ],
        }


class CRUDMediaProcessingJob(
    CRUDBase[MediaProcessingJob, MediaProcessingJob, MediaProcessingJob]
):
    def get_pending_jobs(
        self, session: Session, queue_name: str = "default", limit: int = 10
    ) -> List[MediaProcessingJob]:
        """Get pending processing jobs."""
        return list(
            session.exec(
                select(MediaProcessingJob)
                .where(
                    MediaProcessingJob.job_status == "queued",
                    MediaProcessingJob.queue_name == queue_name,
                )
                .order_by(
                    desc(MediaProcessingJob.priority), MediaProcessingJob.created_at
                )
                .limit(limit)
            )
        )

    def get_jobs_by_media_file(
        self, session: Session, media_file_id: str
    ) -> List[MediaProcessingJob]:
        """Get all processing jobs for a media file."""
        return list(
            session.exec(
                select(MediaProcessingJob)
                .where(MediaProcessingJob.media_file_id == media_file_id)
                .order_by(desc(MediaProcessingJob.created_at))
            )
        )

    def update_job_status(
        self,
        session: Session,
        job_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> Optional[MediaProcessingJob]:
        """Update job status."""
        job = session.get(MediaProcessingJob, job_id)
        if job:
            job.job_status = status
            job.updated_at = datetime.utcnow()

            if status == "processing" and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in ["completed", "failed"]:
                job.completed_at = datetime.utcnow()
                if error_message:
                    job.error_message = error_message

            session.add(job)
            session.commit()
            session.refresh(job)
        return job

    def retry_job(self, session: Session, job_id: str) -> Optional[MediaProcessingJob]:
        """Retry a failed job."""
        job = session.get(MediaProcessingJob, job_id)
        if job and job.job_status == "failed" and job.retry_count < job.max_retries:
            job.job_status = "queued"
            job.retry_count += 1
            job.error_message = None
            job.updated_at = datetime.utcnow()
            session.add(job)
            session.commit()
            session.refresh(job)
        return job


class CRUDMediaStorage(CRUDBase[MediaStorage, MediaStorage, MediaStorage]):
    def get_default_storage(self, session: Session) -> Optional[MediaStorage]:
        """Get the default storage configuration."""
        return session.exec(
            select(MediaStorage).where(
                MediaStorage.is_active == True, MediaStorage.is_default == True
            )
        ).first()

    def get_active_storages(self, session: Session) -> List[MediaStorage]:
        """Get all active storage configurations."""
        return list(
            session.exec(
                select(MediaStorage)
                .where(MediaStorage.is_active == True)
                .order_by(desc(MediaStorage.is_default))
            )
        )

    def update_usage(
        self,
        session: Session,
        storage_id: str,
        files_added: int = 0,
        size_added: int = 0,
    ) -> Optional[MediaStorage]:
        """Update storage usage statistics."""
        storage = session.get(MediaStorage, storage_id)
        if storage:
            storage.total_files += files_added
            storage.total_size_bytes += size_added
            storage.monthly_usage_bytes += size_added
            storage.updated_at = datetime.utcnow()
            session.add(storage)
            session.commit()
            session.refresh(storage)
        return storage


class CRUDMediaAnalytics(CRUDBase[MediaAnalytics, MediaAnalytics, MediaAnalytics]):
    def get_analytics_for_media(
        self,
        session: Session,
        media_file_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MediaAnalytics]:
        """Get analytics for a specific media file."""
        query = select(MediaAnalytics).where(
            MediaAnalytics.media_file_id == media_file_id
        )

        if start_date:
            query = query.where(MediaAnalytics.date_recorded >= start_date)
        if end_date:
            query = query.where(MediaAnalytics.date_recorded <= end_date)

        return list(session.exec(query.order_by(MediaAnalytics.date_recorded)))

    def update_analytics(
        self, session: Session, media_file_id: str, metrics: Dict[str, Any]
    ) -> MediaAnalytics:
        """Update or create analytics for today."""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Try to get existing analytics for today
        analytics = session.exec(
            select(MediaAnalytics).where(
                MediaAnalytics.media_file_id == media_file_id,
                MediaAnalytics.date_recorded >= today,
                MediaAnalytics.date_recorded < today + timedelta(days=1),
            )
        ).first()

        if analytics:
            # Update existing
            for key, value in metrics.items():
                if hasattr(analytics, key):
                    setattr(analytics, key, value)
        else:
            # Create new
            analytics = MediaAnalytics(
                media_file_id=media_file_id,
                date_recorded=datetime.utcnow(),
                week_start=week_start,
                month_start=month_start,
                **metrics,
            )
            session.add(analytics)

        session.commit()
        session.refresh(analytics)
        return analytics


crud_media_file = CRUDMediaFile(MediaFile)
crud_media_processing_job = CRUDMediaProcessingJob(MediaProcessingJob)
crud_media_storage = CRUDMediaStorage(MediaStorage)
crud_media_analytics = CRUDMediaAnalytics(MediaAnalytics)
