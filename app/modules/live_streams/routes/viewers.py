from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.modules.live_streams.schema.viewer import (
    StreamViewerList,
    StreamViewerPublic,
    StreamViewerStats,
)
from app.modules.live_streams.services.viewer_service import stream_viewer_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/{stream_id}/join")
def join_stream(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    device_type: str = Query(None, description="Device type (mobile, desktop, tablet)"),
    browser: str = Query(None, description="Browser name"),
    location: str = Query(None, description="User location/country"),
) -> dict:
    """Join a live stream"""
    # Check if stream exists and is live
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if not stream.is_live:
        raise HTTPException(status_code=400, detail="Stream is not currently live")

    viewer = stream_viewer_service.join_stream(
        session,
        stream_id=stream_id,
        user_id=current_user.id,
        device_type=device_type,
        browser=browser,
        location=location,
    )

    # Update stream viewer count
    active_viewers = stream_viewer_service.get_active_viewers(session, stream_id)
    stream_service.update_viewer_count(session, stream_id, len(active_viewers))

    return {"message": "Joined stream successfully", "viewer_id": viewer.id}


@router.post("/{stream_id}/leave")
def leave_stream(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Leave a live stream"""
    viewer = stream_viewer_service.leave_stream(
        session, stream_id=stream_id, user_id=current_user.id
    )
    if not viewer:
        raise HTTPException(status_code=404, detail="Viewer not found")

    # Update stream viewer count
    from app.modules.live_streams.services.stream_service import stream_service

    active_viewers = stream_viewer_service.get_active_viewers(session, stream_id)
    stream_service.update_viewer_count(session, stream_id, len(active_viewers))

    return {"message": "Left stream successfully"}


@router.get("/{stream_id}/viewers", response_model=StreamViewerList)
def get_stream_viewers(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(False, description="Only return active viewers"),
) -> StreamViewerList:
    """Get viewers for a stream"""
    # Check stream ownership
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view viewers")

    if active_only:
        viewers = stream_viewer_service.get_active_viewers(session, stream_id)
    else:
        viewers = stream_viewer_service.get_stream_viewers(session, stream_id)

    total = len(viewers)
    viewers_paginated = viewers[skip : skip + limit]

    return StreamViewerList(
        data=[
            StreamViewerPublic.model_validate(viewer) for viewer in viewers_paginated
        ],
        total=total,
        page=skip // limit + 1,
        size=len(viewers_paginated),
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.put("/viewer/{viewer_id}/role")
def update_viewer_role(
    viewer_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    role: str = Query(..., description="New role (viewer, moderator, host)"),
) -> dict:
    """Update viewer role (moderator action)"""
    viewer = stream_viewer_service.get_viewer(session, viewer_id)
    if not viewer:
        raise HTTPException(status_code=404, detail="Viewer not found")

    # Check if current user is stream owner or moderator
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, viewer.stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    # Check permissions
    is_owner = stream.user_id == current_user.id
    is_moderator = any(
        v.user_id == current_user.id and v.role.value == "moderator"
        for v in stream_viewer_service.get_moderators(session, viewer.stream_id)
    )

    if not (is_owner or is_moderator):
        raise HTTPException(status_code=403, detail="Not authorized to manage viewers")

    updated_viewer = stream_viewer_service.update_viewer_role(session, viewer_id, role)
    if not updated_viewer:
        raise HTTPException(status_code=400, detail="Failed to update viewer role")

    return {"message": f"Viewer role updated to {role}"}


@router.post("/viewer/{viewer_id}/ban")
def ban_viewer(
    viewer_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Ban a viewer from the stream"""
    viewer = stream_viewer_service.get_viewer(session, viewer_id)
    if not viewer:
        raise HTTPException(status_code=404, detail="Viewer not found")

    # Check permissions (same as above)
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, viewer.stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    is_owner = stream.user_id == current_user.id
    is_moderator = any(
        v.user_id == current_user.id and v.role.value == "moderator"
        for v in stream_viewer_service.get_moderators(session, viewer.stream_id)
    )

    if not (is_owner or is_moderator):
        raise HTTPException(status_code=403, detail="Not authorized to ban viewers")

    banned_viewer = stream_viewer_service.ban_viewer(session, viewer_id)
    if not banned_viewer:
        raise HTTPException(status_code=400, detail="Failed to ban viewer")

    return {"message": "Viewer banned successfully"}


@router.post("/viewer/{viewer_id}/mute")
def mute_viewer(
    viewer_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Mute a viewer in the stream"""
    viewer = stream_viewer_service.get_viewer(session, viewer_id)
    if not viewer:
        raise HTTPException(status_code=404, detail="Viewer not found")

    # Check permissions
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, viewer.stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    is_owner = stream.user_id == current_user.id
    is_moderator = any(
        v.user_id == current_user.id and v.role.value == "moderator"
        for v in stream_viewer_service.get_moderators(session, viewer.stream_id)
    )

    if not (is_owner or is_moderator):
        raise HTTPException(status_code=403, detail="Not authorized to mute viewers")

    muted_viewer = stream_viewer_service.mute_viewer(session, viewer_id)
    if not muted_viewer:
        raise HTTPException(status_code=400, detail="Failed to mute viewer")

    return {"message": "Viewer muted successfully"}


@router.get("/{stream_id}/stats", response_model=StreamViewerStats)
def get_viewer_stats(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamViewerStats:
    """Get viewer statistics for a stream"""
    # Check stream ownership
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view stats")

    stats = stream_viewer_service.get_viewer_stats(session, stream_id)
    return StreamViewerStats(**stats)
