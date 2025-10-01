from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.modules.media.crud import (
    crud_media_file,
    crud_media_processing_job,
    crud_media_storage,
)
from app.modules.media.model import MediaFile, MediaProcessingJob, MediaStorage
from app.modules.media.schema import (
    MediaFileCreate,
    MediaFilePublic,
    MediaFileUpdate,
    MediaProcessingJobPublic,
    MediaStorageCreate,
    MediaStoragePublic,
    MediaUploadResponse,
    ProcessingJobCreate,
    ProcessingJobUpdate,
)
from app.modules.media.services import media_service
from app.shared.deps.deps import CurrentUser, SessionDep, get_current_active_superuser

router = APIRouter()


@router.post("/upload", response_model=MediaUploadResponse)
def upload_media_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_public: bool = Form(True),
    media_type: Optional[str] = Form(None),
) -> MediaUploadResponse:
    """
    Upload a media file.
    """
    try:
        # Parse tags if provided
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []

        # Create upload request
        upload_request = MediaFileCreate(
            title=title,
            description=description,
            tags=tag_list,
            is_public=is_public,
            media_type=media_type,
        )

        return media_service.upload_file(
            session=session,
            file=file,
            upload_request=upload_request,
            user_id=current_user.id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Upload failed: {str(e)}"
        )


@router.get("/", response_model=List[MediaFilePublic])
def read_media_files(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    media_type: Optional[str] = None,
    user_id: Optional[UUID] = None,
    is_public: Optional[bool] = None,
) -> List[MediaFile]:
    """
    Retrieve media files with optional filtering.
    """
    if user_id and user_id != current_user.id:
        # Only allow users to see their own files or public files
        is_public = True

    files = crud_media_file.get_multi(
        session=session,
        skip=skip,
        limit=limit,
        media_type=media_type,
        user_id=user_id or current_user.id,
        is_public=is_public,
    )
    return files


@router.get("/{file_id}", response_model=MediaFilePublic)
def read_media_file(
    *, session: SessionDep, current_user: CurrentUser, file_id: str
) -> MediaFile:
    """
    Get a specific media file by ID.
    """
    file = crud_media_file.get(session=session, id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Media file not found")

    # Check permissions
    if not file.is_public and file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return file


@router.put("/{file_id}", response_model=MediaFilePublic)
def update_media_file(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file_id: str,
    file_in: MediaFileUpdate,
) -> MediaFile:
    """
    Update a media file.
    """
    file = crud_media_file.get(session=session, id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Media file not found")

    if file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    file = media_service.update_media_file(
        session=session, file_id=file_id, updates=file_in
    )
    return file


@router.delete("/{file_id}")
def delete_media_file(
    *, session: SessionDep, current_user: CurrentUser, file_id: str
) -> dict:
    """
    Delete a media file.
    """
    file = crud_media_file.get(session=session, id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Media file not found")

    if file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud_media_file.remove(session=session, id=file_id)
    return {"message": "Media file deleted successfully"}


# Processing Jobs Routes


@router.post("/jobs", response_model=MediaProcessingJobPublic)
def create_processing_job(
    *, session: SessionDep, current_user: CurrentUser, job_in: ProcessingJobCreate
) -> MediaProcessingJob:
    """
    Create a new processing job.
    """
    return crud_media_processing_job.create(session=session, obj_in=job_in)


@router.get("/jobs", response_model=List[MediaProcessingJobPublic])
def read_processing_jobs(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    file_id: Optional[str] = None,
) -> List[MediaProcessingJob]:
    """
    Retrieve processing jobs with optional filtering.
    """
    jobs = crud_media_processing_job.get_multi(
        session=session, skip=skip, limit=limit, status=status_filter, file_id=file_id
    )
    return jobs


@router.get("/jobs/{job_id}", response_model=MediaProcessingJobPublic)
def read_processing_job(
    *, session: SessionDep, current_user: CurrentUser, job_id: str
) -> MediaProcessingJob:
    """
    Get a specific processing job by ID.
    """
    job = crud_media_processing_job.get(session=session, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return job


@router.put("/jobs/{job_id}", response_model=MediaProcessingJobPublic)
def update_processing_job(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    job_id: str,
    job_in: ProcessingJobUpdate,
) -> MediaProcessingJob:
    """
    Update a processing job.
    """
    job = crud_media_processing_job.get(session=session, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")

    job = crud_media_processing_job.update(session=session, db_obj=job, obj_in=job_in)
    return job


# Storage Management Routes (Admin only)


@router.post("/storage", response_model=MediaStoragePublic)
def create_storage_config(
    *, session: SessionDep, current_user: CurrentUser, storage_in: MediaStorageCreate
) -> MediaStorage:
    """
    Create a new storage configuration (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return media_service.create_storage(session=session, storage_data=storage_in)


@router.get("/storage", response_model=List[MediaStoragePublic])
def read_storage_configs(
    *, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[MediaStorage]:
    """
    Retrieve storage configurations (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    storages = crud_media_storage.get_multi(session=session, skip=skip, limit=limit)
    return storages


@router.get("/storage/stats")
def get_storage_stats(*, session: SessionDep, current_user: CurrentUser) -> dict:
    """
    Get storage usage statistics (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    stats = crud_media_storage.get_storage_stats(session=session)
    return stats
