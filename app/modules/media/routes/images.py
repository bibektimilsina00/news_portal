from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.modules.media.crud import crud_media_file
from app.modules.media.model import MediaFile
from app.modules.media.schema import (
    ImageCropRequest,
    ImageResizeRequest,
    MediaFilePublic,
)
from app.modules.media.services import media_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/", response_model=List[MediaFilePublic])
def read_images(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    is_public: Optional[bool] = None,
) -> List[MediaFile]:
    """
    Retrieve images with optional filtering.
    """
    if user_id and user_id != str(current_user.id):
        # Only allow users to see their own images or public images
        is_public = True

    images = crud_media_file.get_multi(
        session=session,
        skip=skip,
        limit=limit,
        media_type="image",
        user_id=user_id or str(current_user.id),
        is_public=is_public,
    )
    return images


@router.post("/{image_id}/resize")
def resize_image(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    image_id: str,
    resize_request: ImageResizeRequest,
) -> dict:
    """
    Create a processing job to resize an image.
    """
    # Check if image exists and user has access
    image = crud_media_file.get(session=session, id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.media_type != "image":
        raise HTTPException(status_code=400, detail="File is not an image")

    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        job = media_service.create_resize_job(
            session=session,
            image_id=image_id,
            width=resize_request.width,
            height=resize_request.height,
            maintain_aspect_ratio=resize_request.maintain_aspect_ratio,
        )
        return {"message": "Image resize job created successfully", "job_id": job.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resize job creation failed: {str(e)}",
        )


@router.post("/{image_id}/crop")
def crop_image(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    image_id: str,
    crop_request: ImageCropRequest,
) -> dict:
    """
    Create a processing job to crop an image.
    """
    # Check if image exists and user has access
    image = crud_media_file.get(session=session, id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.media_type != "image":
        raise HTTPException(status_code=400, detail="File is not an image")

    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        job = media_service.create_crop_job(
            session=session,
            image_id=image_id,
            x=crop_request.x,
            y=crop_request.y,
            width=crop_request.width,
            height=crop_request.height,
        )
        return {"message": "Image crop job created successfully", "job_id": job.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Crop job creation failed: {str(e)}",
        )


@router.post("/{image_id}/convert")
def convert_image_format(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    image_id: str,
    target_format: str = Query(..., description="Target format (jpg, png, webp, etc.)"),
) -> dict:
    """
    Create a processing job to convert image format.
    """
    # Check if image exists and user has access
    image = crud_media_file.get(session=session, id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.media_type != "image":
        raise HTTPException(status_code=400, detail="File is not an image")

    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Validate target format
    valid_formats = ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]
    if target_format.lower() not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target format. Supported: {', '.join(valid_formats)}",
        )

    try:
        job = media_service.create_format_conversion_job(
            session=session, image_id=image_id, target_format=target_format.lower()
        )
        return {
            "message": "Image format conversion job created successfully",
            "job_id": job.id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format conversion job creation failed: {str(e)}",
        )


@router.post("/{image_id}/optimize")
def optimize_image(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    image_id: str,
    quality: Optional[int] = Query(
        85, description="Quality level (1-100)", ge=1, le=100
    ),
) -> dict:
    """
    Create a processing job to optimize image for web.
    """
    # Check if image exists and user has access
    image = crud_media_file.get(session=session, id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.media_type != "image":
        raise HTTPException(status_code=400, detail="File is not an image")

    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        job = media_service.create_optimization_job(
            session=session, image_id=image_id, quality=quality
        )
        return {
            "message": "Image optimization job created successfully",
            "job_id": job.id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Optimization job creation failed: {str(e)}",
        )
