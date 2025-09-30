from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.modules.live_streams.schema.stream import (
    StreamAnalytics,
    StreamCreate,
    StreamEnd,
    StreamList,
    StreamPublic,
    StreamUpdate,
)
from app.modules.live_streams.services.stream_service import stream_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=StreamPublic)
def create_stream(
    stream_data: StreamCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamPublic:
    """Create a new live stream"""
    stream = stream_service.create_stream(session, current_user.id, stream_data)
    return StreamPublic.model_validate(stream)


@router.get("/", response_model=StreamList)
def get_streams(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> StreamList:
    """Get user's streams"""
    streams = stream_service.get_user_streams(session, current_user.id)
    total = len(streams)

    # Apply pagination
    streams_paginated = streams[skip : skip + limit]

    return StreamList(
        data=[StreamPublic.model_validate(stream) for stream in streams_paginated],
        total=total,
        page=skip // limit + 1,
        size=len(streams_paginated),
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/live", response_model=List[StreamPublic])
def get_live_streams(
    session: SessionDep,
) -> List[StreamPublic]:
    """Get all currently live streams"""
    streams = stream_service.get_live_streams(session)
    return [StreamPublic.model_validate(stream) for stream in streams]


@router.get("/{stream_id}", response_model=StreamPublic)
def get_stream(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamPublic:
    """Get stream by ID"""
    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    # Check if user owns the stream or it's public
    if stream.user_id != current_user.id and stream.visibility.value == "private":
        raise HTTPException(
            status_code=403, detail="Not authorized to view this stream"
        )

    return StreamPublic.model_validate(stream)


@router.put("/{stream_id}", response_model=StreamPublic)
def update_stream(
    stream_id: UUID,
    stream_data: StreamUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamPublic:
    """Update stream details"""
    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this stream"
        )

    updated_stream = stream_service.update_stream(session, stream_id, stream_data)
    if not updated_stream:
        raise HTTPException(status_code=400, detail="Failed to update stream")

    return StreamPublic.model_validate(updated_stream)


@router.delete("/{stream_id}")
def delete_stream(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Delete a stream"""
    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this stream"
        )

    success = stream_service.delete_stream(session, stream_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete stream")

    return {"message": "Stream deleted successfully"}


@router.post("/{stream_id}/start", response_model=StreamPublic)
def start_stream(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamPublic:
    """Start a live stream"""
    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to start this stream"
        )

    started_stream = stream_service.start_stream(session, stream_id)
    if not started_stream:
        raise HTTPException(status_code=400, detail="Failed to start stream")

    return StreamPublic.model_validate(started_stream)


@router.post("/{stream_id}/end", response_model=StreamPublic)
def end_stream(
    stream_id: UUID,
    end_data: StreamEnd,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamPublic:
    """End a live stream"""
    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to end this stream")

    ended_stream = stream_service.end_stream(session, stream_id)
    if not ended_stream:
        raise HTTPException(status_code=400, detail="Failed to end stream")

    return StreamPublic.model_validate(ended_stream)


@router.get("/{stream_id}/analytics", response_model=StreamAnalytics)
def get_stream_analytics(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamAnalytics:
    """Get stream analytics"""
    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view analytics")

    analytics = stream_service.get_stream_analytics(session, stream_id)
    return StreamAnalytics(**analytics)
