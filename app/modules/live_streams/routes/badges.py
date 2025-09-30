from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.modules.live_streams.schema.badge import (
    StreamBadgeList,
    StreamBadgePublic,
    StreamBadgeStats,
)
from app.modules.live_streams.services.badge_service import stream_badge_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/{stream_id}/donate")
def send_donation(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    amount: float = Query(..., ge=0.01, description="Donation amount"),
    badge_type: str = Query(
        "heart", description="Badge type (heart, star, diamond, etc.)"
    ),
    message: str = Query(None, max_length=500, description="Optional donation message"),
) -> dict:
    """Send a donation/badge to a stream"""
    # Check if stream exists and is live
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if not stream.is_live:
        raise HTTPException(status_code=400, detail="Stream is not currently live")

    try:
        badge = stream_badge_service.process_donation(
            session,
            stream_id=stream_id,
            sender_id=current_user.id,
            amount=amount,
            badge_type=badge_type,
            message=message,
        )
        return {
            "message": "Donation sent successfully",
            "badge_id": badge.id,
            "amount": amount,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{stream_id}/badges", response_model=StreamBadgeList)
def get_stream_badges(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    recent: bool = Query(False, description="Get only recent badges"),
) -> StreamBadgeList:
    """Get badges/donations for a stream"""
    # Check stream ownership or public visibility
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id and stream.visibility.value == "private":
        raise HTTPException(status_code=403, detail="Not authorized to view badges")

    if recent:
        badges = stream_badge_service.get_recent_badges(session, stream_id, limit=limit)
        total = len(badges)  # Approximate
    else:
        badges = stream_badge_service.get_stream_badges(session, stream_id)
        total = len(badges)
        badges = badges[skip : skip + limit]

    return StreamBadgeList(
        data=[StreamBadgePublic.model_validate(badge) for badge in badges],
        total=total,
        page=skip // limit + 1 if not recent else 1,
        size=len(badges),
        has_next=(skip + limit) < total if not recent else False,
        has_prev=skip > 0 if not recent else False,
    )


@router.get("/user/{user_id}/badges", response_model=List[StreamBadgePublic])
def get_user_badges(
    user_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=200),
) -> List[StreamBadgePublic]:
    """Get badges sent by a user"""
    # Users can only see their own badges
    if user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view other users' badges"
        )

    badges = stream_badge_service.get_user_badges(session, user_id)
    # Return most recent first
    badges = badges[-limit:] if len(badges) > limit else badges

    return [StreamBadgePublic.model_validate(badge) for badge in badges]


@router.get("/{stream_id}/badges/{badge_type}", response_model=List[StreamBadgePublic])
def get_badges_by_type(
    stream_id: UUID,
    badge_type: str,
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=200),
) -> List[StreamBadgePublic]:
    """Get badges of specific type for a stream"""
    # Check stream access
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id and stream.visibility.value == "private":
        raise HTTPException(status_code=403, detail="Not authorized to view badges")

    badges = stream_badge_service.get_badges_by_type(session, stream_id, badge_type)
    badges = badges[-limit:] if len(badges) > limit else badges

    return [StreamBadgePublic.model_validate(badge) for badge in badges]


@router.get("/{stream_id}/donations/total")
def get_total_donations(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Get total donation amount for a stream"""
    # Check stream ownership
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view donation totals"
        )

    total = stream_badge_service.get_total_donations(session, stream_id)
    return {"stream_id": stream_id, "total_donations": total}


@router.get("/{stream_id}/leaderboard")
def get_donation_leaderboard(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """Get donation leaderboard for a stream"""
    # Check stream access
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id and stream.visibility.value == "private":
        raise HTTPException(
            status_code=403, detail="Not authorized to view leaderboard"
        )

    leaderboard = stream_badge_service.get_donation_leaderboard(session, stream_id)
    return {
        "stream_id": stream_id,
        "leaderboard": leaderboard,
        "total_donors": len(leaderboard),
    }


@router.get("/{stream_id}/badges/stats", response_model=StreamBadgeStats)
def get_badge_stats(
    stream_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamBadgeStats:
    """Get badge statistics for a stream"""
    # Check stream ownership
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view badge stats"
        )

    stats = stream_badge_service.get_badge_stats(session, stream_id)
    return StreamBadgeStats(**stats)


@router.delete("/badge/{badge_id}")
def delete_badge(
    badge_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict:
    """Delete a badge (admin/stream owner only)"""
    badge = stream_badge_service.get_badge(session, badge_id)
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    # Check stream ownership
    from app.modules.live_streams.services.stream_service import stream_service

    stream = stream_service.get_stream(session, badge.stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    if stream.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete badges")

    success = stream_badge_service.delete_badge(session, badge_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete badge")

    return {"message": "Badge deleted successfully"}
