from typing import Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.live_streams.crud.crud_viewer import crud_stream_viewer
from app.modules.live_streams.model.viewer import StreamViewer
from app.modules.live_streams.schema.viewer import (
    StreamViewerCreate,
    StreamViewerUpdate,
)


class StreamViewerService:
    """Business logic for stream viewers"""

    @staticmethod
    def join_stream(
        session: Session,
        stream_id: UUID,
        user_id: UUID,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        location: Optional[str] = None,
    ) -> StreamViewer:
        """User joins a stream"""
        return crud_stream_viewer.join_stream(
            session,
            stream_id=stream_id,
            user_id=user_id,
            device_type=device_type,
            browser=browser,
            location=location,
        )

    @staticmethod
    def leave_stream(
        session: Session, stream_id: UUID, user_id: UUID
    ) -> Optional[StreamViewer]:
        """User leaves a stream"""
        return crud_stream_viewer.leave_stream(
            session, stream_id=stream_id, user_id=user_id
        )

    @staticmethod
    def get_stream_viewers(session: Session, stream_id: UUID) -> list[StreamViewer]:
        """Get all viewers for a stream"""
        return crud_stream_viewer.get_by_stream_id(session, stream_id=stream_id)

    @staticmethod
    def get_active_viewers(session: Session, stream_id: UUID) -> list[StreamViewer]:
        """Get active viewers for a stream"""
        return crud_stream_viewer.get_active_viewers(session, stream_id=stream_id)

    @staticmethod
    def get_viewer(session: Session, viewer_id: UUID) -> Optional[StreamViewer]:
        """Get viewer by ID"""
        return crud_stream_viewer.get(session, viewer_id)

    @staticmethod
    def update_viewer_role(
        session: Session, viewer_id: UUID, role: str
    ) -> Optional[StreamViewer]:
        """Update viewer role (moderator, etc.)"""
        from app.modules.live_streams.model.viewer import ViewerRole

        viewer = crud_stream_viewer.get(session, viewer_id)
        if viewer:
            update_data = StreamViewerUpdate(role=ViewerRole(role))
            return crud_stream_viewer.update(session, db_obj=viewer, obj_in=update_data)
        return None

    @staticmethod
    def ban_viewer(session: Session, viewer_id: UUID) -> Optional[StreamViewer]:
        """Ban a viewer from the stream"""
        return crud_stream_viewer.ban_viewer(session, viewer_id=viewer_id)

    @staticmethod
    def unban_viewer(session: Session, viewer_id: UUID) -> Optional[StreamViewer]:
        """Unban a viewer from the stream"""
        return crud_stream_viewer.unban_viewer(session, viewer_id=viewer_id)

    @staticmethod
    def mute_viewer(session: Session, viewer_id: UUID) -> Optional[StreamViewer]:
        """Mute a viewer in the stream"""
        return crud_stream_viewer.mute_viewer(session, viewer_id=viewer_id)

    @staticmethod
    def unmute_viewer(session: Session, viewer_id: UUID) -> Optional[StreamViewer]:
        """Unmute a viewer in the stream"""
        return crud_stream_viewer.unmute_viewer(session, viewer_id=viewer_id)

    @staticmethod
    def update_engagement(
        session: Session,
        viewer_id: UUID,
        comments: int = 0,
        reactions: int = 0,
        badges: int = 0,
    ) -> Optional[StreamViewer]:
        """Update viewer engagement metrics"""
        return crud_stream_viewer.update_engagement(
            session,
            viewer_id=viewer_id,
            comments=comments,
            reactions=reactions,
            badges=badges,
        )

    @staticmethod
    def get_moderators(session: Session, stream_id: UUID) -> list[StreamViewer]:
        """Get stream moderators"""
        return crud_stream_viewer.get_moderators(session, stream_id=stream_id)

    @staticmethod
    def get_banned_viewers(session: Session, stream_id: UUID) -> list[StreamViewer]:
        """Get banned viewers for a stream"""
        return crud_stream_viewer.get_banned_viewers(session, stream_id=stream_id)

    @staticmethod
    def get_viewer_stats(session: Session, stream_id: UUID) -> dict:
        """Get viewer statistics for a stream"""
        viewers = crud_stream_viewer.get_by_stream_id(session, stream_id)

        active_viewers = [v for v in viewers if v.is_active]
        total_sessions = len(viewers)
        unique_users = len(set(str(v.user_id) for v in viewers))

        # Calculate average session duration
        durations = [v.session_duration for v in viewers if v.session_duration]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Device breakdown
        device_breakdown = {}
        for viewer in viewers:
            device = getattr(viewer, "device_type", "unknown") or "unknown"
            device_breakdown[device] = device_breakdown.get(device, 0) + 1

        return {
            "stream_id": stream_id,
            "total_sessions": total_sessions,
            "unique_users": unique_users,
            "active_viewers": len(active_viewers),
            "average_session_duration": avg_duration,
            "device_breakdown": device_breakdown,
            "moderators_count": len(
                [v for v in active_viewers if v.role.value == "moderator"]
            ),
            "banned_count": len([v for v in viewers if v.is_banned]),
        }


stream_viewer_service = StreamViewerService()
