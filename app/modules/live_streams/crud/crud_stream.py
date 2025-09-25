from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.live_streams.model.stream import Stream
from app.modules.live_streams.schema.stream import StreamCreate, StreamUpdate
from app.shared.crud.base import CRUDBase


class CRUDStream(CRUDBase[Stream, StreamCreate, StreamUpdate]):
    """CRUD operations for streams"""

    def get_by_user_id(self, session: Session, user_id: UUID) -> list[Stream]:
        """Get all streams by user ID"""
        return list(session.exec(select(Stream).where(Stream.user_id == user_id)).all())

    def get_live_streams(self, session: Session) -> list[Stream]:
        """Get all currently live streams"""
        return list(session.exec(select(Stream).where(Stream.status == "live")).all())

    def get_scheduled_streams(self, session: Session) -> list[Stream]:
        """Get all scheduled streams"""
        return list(
            session.exec(select(Stream).where(Stream.status == "scheduled")).all()
        )

    def get_by_stream_key(self, session: Session, stream_key: str) -> Optional[Stream]:
        """Get stream by stream key"""
        return session.exec(
            select(Stream).where(Stream.stream_key == stream_key)
        ).first()

    def update_viewer_count(
        self, session: Session, stream_id: UUID, count: int
    ) -> Optional[Stream]:
        """Update current viewer count"""
        stream = self.get(session, stream_id)
        if stream:
            stream.current_viewers = count
            session.add(stream)
            session.commit()
            session.refresh(stream)
        return stream

    def increment_analytics(
        self,
        session: Session,
        stream_id: UUID,
        viewers: int = 0,
        comments: int = 0,
        reactions: int = 0,
        badges: int = 0,
        donations: float = 0.0,
    ) -> Optional[Stream]:
        """Increment analytics counters"""
        stream = self.get(session, stream_id)
        if stream:
            stream.total_viewers += viewers
            stream.total_comments += comments
            stream.total_reactions += reactions
            stream.total_badges += badges
            stream.total_donations += donations

            # Update peak viewers
            if stream.current_viewers > stream.peak_viewers:
                stream.peak_viewers = stream.current_viewers

            session.add(stream)
            session.commit()
            session.refresh(stream)
        return stream

    def start_stream(self, session: Session, stream_id: UUID) -> Optional[Stream]:
        """Mark stream as started"""
        from app.modules.live_streams.model.stream import StreamStatus

        stream = self.get(session, stream_id)
        if stream and stream.status in [StreamStatus.SCHEDULED, StreamStatus.ENDED]:
            stream.status = StreamStatus.LIVE
            stream.started_at = datetime.utcnow()
            session.add(stream)
            session.commit()
            session.refresh(stream)
        return stream

    def end_stream(self, session: Session, stream_id: UUID) -> Optional[Stream]:
        """Mark stream as ended"""
        from app.modules.live_streams.model.stream import StreamStatus

        stream = self.get(session, stream_id)
        if stream and stream.status == StreamStatus.LIVE:
            stream.status = StreamStatus.ENDED
            stream.ended_at = datetime.utcnow()
            session.add(stream)
            session.commit()
            session.refresh(stream)
        return stream


crud_stream = CRUDStream(Stream)
