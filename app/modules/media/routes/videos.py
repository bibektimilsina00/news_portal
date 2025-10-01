from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.modules.media.crud import crud_media_file
from app.modules.media.model import MediaFile
from app.modules.media.schema import (
    MediaFilePublic,
    VideoCompressRequest,
    VideoTrimRequest,
)
from app.modules.media.services import media_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/", response_model=List[MediaFilePublic])
def read_videos(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    is_public: Optional[bool] = None,
) -> List[MediaFile]:
    """
    Retrieve videos with optional filtering.
    """
    if user_id and user_id != str(current_user.id):
        # Only allow users to see their own videos or public videos
        is_public = True

    videos = crud_media_file.get_multi(
        session=session,
        skip=skip,
        limit=limit,
        media_type="video",
        user_id=user_id or str(current_user.id),
        is_public=is_public,
    )
    return videos


@router.post("/{video_id}/compress")
def compress_video(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    video_id: str,
    compress_request: VideoCompressRequest,
) -> dict:
    """
    Create a processing job to compress a video.
    """
    # Check if video exists and user has access
    video = crud_media_file.get(session=session, id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.media_type != "video":
        raise HTTPException(status_code=400, detail="File is not a video")

    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        job = media_service.create_video_compress_job(
            session=session,
            video_id=video_id,
            target_bitrate=compress_request.target_bitrate,
            target_resolution=compress_request.target_resolution,
            preset=compress_request.preset,
        )
        return {
            "message": "Video compression job created successfully",
            "job_id": job.id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Compression job creation failed: {str(e)}",
        )


@router.post("/{video_id}/trim")
def trim_video(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    video_id: str,
    trim_request: VideoTrimRequest,
) -> dict:
    """
    Create a processing job to trim a video.
    """
    # Check if video exists and user has access
    video = crud_media_file.get(session=session, id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.media_type != "video":
        raise HTTPException(status_code=400, detail="File is not a video")

    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Validate time ranges
    if trim_request.start_time >= trim_request.end_time:
        raise HTTPException(
            status_code=400, detail="Start time must be less than end time"
        )

    try:
        job = media_service.create_video_trim_job(
            session=session,
            video_id=video_id,
            start_time=trim_request.start_time,
            end_time=trim_request.end_time,
        )
        return {"message": "Video trim job created successfully", "job_id": job.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trim job creation failed: {str(e)}",
        )


@router.post("/{video_id}/thumbnail")
def generate_video_thumbnail(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    video_id: str,
    timestamp: Optional[float] = Query(
        1.0, description="Timestamp in seconds for thumbnail", ge=0
    ),
) -> dict:
    """
    Create a processing job to generate video thumbnail.
    """
    # Check if video exists and user has access
    video = crud_media_file.get(session=session, id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.media_type != "video":
        raise HTTPException(status_code=400, detail="File is not a video")

    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        job = media_service.create_video_thumbnail_job(
            session=session, video_id=video_id, timestamp=timestamp
        )
        return {
            "message": "Video thumbnail generation job created successfully",
            "job_id": job.id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Thumbnail job creation failed: {str(e)}",
        )


@router.post("/{video_id}/convert")
def convert_video_format(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    video_id: str,
    target_format: str = Query(..., description="Target format (mp4, webm, avi, etc.)"),
) -> dict:
    """
    Create a processing job to convert video format.
    """
    # Check if video exists and user has access
    video = crud_media_file.get(session=session, id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.media_type != "video":
        raise HTTPException(status_code=400, detail="File is not a video")

    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Validate target format
    valid_formats = ["mp4", "webm", "avi", "mov", "mkv", "flv", "wmv"]
    if target_format.lower() not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target format. Supported: {', '.join(valid_formats)}",
        )

    try:
        job = media_service.create_video_format_conversion_job(
            session=session, video_id=video_id, target_format=target_format.lower()
        )
        return {
            "message": "Video format conversion job created successfully",
            "job_id": job.id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format conversion job creation failed: {str(e)}",
        )


@router.post("/{video_id}/extract-audio")
def extract_audio_from_video(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    video_id: str,
    audio_format: str = Query("mp3", description="Audio format (mp3, wav, aac, etc.)"),
) -> dict:
    """
    Create a processing job to extract audio from video.
    """
    # Check if video exists and user has access
    video = crud_media_file.get(session=session, id=video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.media_type != "video":
        raise HTTPException(status_code=400, detail="File is not a video")

    if video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Validate audio format
    valid_formats = ["mp3", "wav", "aac", "ogg", "flac", "m4a"]
    if audio_format.lower() not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio format. Supported: {', '.join(valid_formats)}",
        )

    try:
        job = media_service.create_audio_extraction_job(
            session=session, video_id=video_id, audio_format=audio_format.lower()
        )
        return {
            "message": "Audio extraction job created successfully",
            "job_id": job.id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Audio extraction job creation failed: {str(e)}",
        )
