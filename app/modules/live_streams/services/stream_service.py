from typing import Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.live_streams.crud.crud_badge import crud_stream_badge
from app.modules.live_streams.crud.crud_stream import crud_stream
from app.modules.live_streams.crud.crud_viewer import crud_stream_viewer
from app.modules.live_streams.model.stream import Stream
from app.modules.live_streams.schema.stream import (
    StreamCreate,
    StreamUpdate,
)


class StreamService:
    """Business logic for live streams"""

    @staticmethod
    def create_stream(
        session: Session, user_id: UUID, stream_data: StreamCreate
    ) -> Stream:
        """Create a new stream"""
        import secrets

        # Generate unique stream key
        stream_key = secrets.token_urlsafe(32)

        # Create stream with generated key
        stream_dict = stream_data.model_dump()
        stream_dict["user_id"] = user_id
        stream_dict["stream_key"] = stream_key

        stream_create = StreamCreate(**stream_dict)
        stream = crud_stream.create(session, obj_in=stream_create)
        return stream

    @staticmethod
    def get_stream(session: Session, stream_id: UUID) -> Optional[Stream]:
        """Get stream by ID"""
        return crud_stream.get(session, id=stream_id)

    @staticmethod
    def get_user_streams(session: Session, user_id: UUID) -> list[Stream]:
        """Get all streams for a user"""
        return crud_stream.get_by_user_id(session, user_id=user_id)

    @staticmethod
    def update_stream(
        session: Session, stream_id: UUID, update_data: StreamUpdate
    ) -> Optional[Stream]:
        """Update stream details"""
        stream = crud_stream.get(session, stream_id)
        if stream:
            return crud_stream.update(session, db_obj=stream, obj_in=update_data)
        return None

    @staticmethod
    def delete_stream(session: Session, stream_id: UUID) -> bool:
        """Delete a stream"""
        stream = crud_stream.get(session, stream_id)
        if stream:
            crud_stream.remove(session, id=stream_id)
            return True
        return False

    @staticmethod
    def start_stream(session: Session, stream_id: UUID) -> Optional[Stream]:
        """Start a live stream"""
        return crud_stream.start_stream(session, stream_id=stream_id)

    @staticmethod
    def end_stream(session: Session, stream_id: UUID) -> Optional[Stream]:
        """End a live stream"""
        stream = crud_stream.end_stream(session, stream_id=stream_id)
        if stream:
            # Update final viewer count
            active_viewers = crud_stream_viewer.get_active_viewers(session, stream_id)
            stream.current_viewers = len(active_viewers)
            session.add(stream)
            session.commit()
            session.refresh(stream)
        return stream

    @staticmethod
    def get_live_streams(session: Session) -> list[Stream]:
        """Get all currently live streams"""
        return crud_stream.get_live_streams(session)

    @staticmethod
    def get_stream_by_key(session: Session, stream_key: str) -> Optional[Stream]:
        """Get stream by stream key"""
        return crud_stream.get_by_stream_key(session, stream_key=stream_key)

    @staticmethod
    def update_viewer_count(
        session: Session, stream_id: UUID, count: int
    ) -> Optional[Stream]:
        """Update current viewer count"""
        return crud_stream.update_viewer_count(
            session, stream_id=stream_id, count=count
        )

    @staticmethod
    def increment_stream_analytics(
        session: Session,
        stream_id: UUID,
        viewers: int = 0,
        comments: int = 0,
        reactions: int = 0,
        badges: int = 0,
        donations: float = 0.0,
    ) -> Optional[Stream]:
        """Increment stream analytics"""
        return crud_stream.increment_analytics(
            session,
            stream_id=stream_id,
            viewers=viewers,
            comments=comments,
            reactions=reactions,
            badges=badges,
            donations=donations,
        )

    @staticmethod
    def get_stream_analytics(session: Session, stream_id: UUID) -> dict:
        """Get comprehensive analytics for a stream"""
        stream = crud_stream.get(session, stream_id)
        if not stream:
            return {}

        badges = crud_stream_badge.get_by_stream_id(session, stream_id)
        viewers = crud_stream_viewer.get_by_stream_id(session, stream_id)

        return {
            "stream_id": stream_id,
            "total_viewers": stream.total_viewers,
            "peak_viewers": stream.peak_viewers,
            "current_viewers": stream.current_viewers,
            "total_comments": stream.total_comments,
            "total_reactions": stream.total_reactions,
            "total_badges": len(badges),
            "total_donations": sum(
                badge.amount for badge in badges if badge.amount > 0
            ),
            "unique_viewers": len(set(str(v.user_id) for v in viewers)),
            "average_session_duration": (
                sum(v.session_duration or 0 for v in viewers if v.session_duration)
                / len(viewers)
                if viewers
                else 0
            ),
        }


stream_service = StreamService()
