from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.live_streams.model.viewer import StreamViewer
from app.modules.live_streams.schema.viewer import (
    StreamViewerCreate,
    StreamViewerUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDStreamViewer(CRUDBase[StreamViewer, StreamViewerCreate, StreamViewerUpdate]):
    """CRUD operations for stream viewers"""

    def get_by_stream_id(self, session: Session, stream_id: UUID) -> list[StreamViewer]:
        """Get all viewers for a stream"""
        return list(
            session.exec(
                select(StreamViewer).where(StreamViewer.stream_id == stream_id)
            ).all()
        )

    def get_active_viewers(
        self, session: Session, stream_id: UUID
    ) -> list[StreamViewer]:
        """Get active viewers (haven't left) for a stream"""
        return list(
            session.exec(
                select(StreamViewer).where(
                    StreamViewer.stream_id == stream_id, StreamViewer.left_at.is_(None)
                )
            ).all()
        )

    def get_viewer_by_user_and_stream(
        self, session: Session, user_id: UUID, stream_id: UUID
    ) -> Optional[StreamViewer]:
        """Get viewer record for specific user and stream"""
        return session.exec(
            select(StreamViewer).where(
                StreamViewer.user_id == user_id, StreamViewer.stream_id == stream_id
            )
        ).first()

    def join_stream(
        self,
        session: Session,
        stream_id: UUID,
        user_id: UUID,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        location: Optional[str] = None,
    ) -> StreamViewer:
        """Add user as viewer to stream"""
        # Check if user is already viewing
        existing_viewer = self.get_viewer_by_user_and_stream(
            session, user_id, stream_id
        )

        if existing_viewer:
            # Update existing viewer (rejoin)
            existing_viewer.left_at = None
            existing_viewer.joined_at = datetime.utcnow()
            existing_viewer.device_type = device_type
            existing_viewer.browser = browser
            existing_viewer.location = location
            session.add(existing_viewer)
            session.commit()
            session.refresh(existing_viewer)
            return existing_viewer

        # Create new viewer
        viewer_data = StreamViewerCreate(
            stream_id=stream_id,
            user_id=user_id,
            joined_at=datetime.utcnow(),
            device_type=device_type,
            browser=browser,
            location=location,
        )
        return self.create(session, obj_in=viewer_data)

    def leave_stream(
        self, session: Session, stream_id: UUID, user_id: UUID
    ) -> Optional[StreamViewer]:
        """Mark user as left the stream"""
        viewer = self.get_viewer_by_user_and_stream(session, user_id, stream_id)
        if viewer and viewer.left_at is None:
            viewer.left_at = datetime.utcnow()
            session.add(viewer)
            session.commit()
            session.refresh(viewer)
        return viewer

    def update_engagement(
        self,
        session: Session,
        viewer_id: UUID,
        comments: int = 0,
        reactions: int = 0,
        badges: int = 0,
    ) -> Optional[StreamViewer]:
        """Update viewer engagement metrics"""
        viewer = self.get(session, viewer_id)
        if viewer:
            viewer.comments_count += comments
            viewer.reactions_count += reactions
            viewer.badges_sent += badges
            session.add(viewer)
            session.commit()
            session.refresh(viewer)
        return viewer

    def get_moderators(self, session: Session, stream_id: UUID) -> list[StreamViewer]:
        """Get moderators for a stream"""
        from app.modules.live_streams.model.viewer import ViewerRole

        return list(
            session.exec(
                select(StreamViewer).where(
                    StreamViewer.stream_id == stream_id,
                    StreamViewer.role == ViewerRole.MODERATOR,
                    StreamViewer.left_at.is_(None),
                )
            ).all()
        )

    def get_banned_viewers(
        self, session: Session, stream_id: UUID
    ) -> list[StreamViewer]:
        """Get banned viewers for a stream"""
        return list(
            session.exec(
                select(StreamViewer).where(
                    StreamViewer.stream_id == stream_id, StreamViewer.is_banned == True
                )
            ).all()
        )

    def ban_viewer(self, session: Session, viewer_id: UUID) -> Optional[StreamViewer]:
        """Ban a viewer from the stream"""
        viewer = self.get(session, viewer_id)
        if viewer:
            viewer.is_banned = True
            viewer.left_at = datetime.utcnow()
            session.add(viewer)
            session.commit()
            session.refresh(viewer)
        return viewer

    def unban_viewer(self, session: Session, viewer_id: UUID) -> Optional[StreamViewer]:
        """Unban a viewer from the stream"""
        viewer = self.get(session, viewer_id)
        if viewer:
            viewer.is_banned = False
            session.add(viewer)
            session.commit()
            session.refresh(viewer)
        return viewer

    def mute_viewer(self, session: Session, viewer_id: UUID) -> Optional[StreamViewer]:
        """Mute a viewer in the stream"""
        viewer = self.get(session, viewer_id)
        if viewer:
            viewer.is_muted = True
            session.add(viewer)
            session.commit()
            session.refresh(viewer)
        return viewer

    def unmute_viewer(
        self, session: Session, viewer_id: UUID
    ) -> Optional[StreamViewer]:
        """Unmute a viewer in the stream"""
        viewer = self.get(session, viewer_id)
        if viewer:
            viewer.is_muted = False
            session.add(viewer)
            session.commit()
            session.refresh(viewer)
        return viewer


crud_stream_viewer = CRUDStreamViewer(StreamViewer)
