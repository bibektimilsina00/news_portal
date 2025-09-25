from typing import Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.live_streams.crud.crud_badge import crud_stream_badge
from app.modules.live_streams.model.badge import StreamBadge
from app.modules.live_streams.schema.badge import StreamBadgeCreate


class StreamBadgeService:
    """Business logic for stream badges/donations"""

    @staticmethod
    def send_badge(
        session: Session,
        stream_id: UUID,
        sender_id: UUID,
        badge_type: str,
        amount: float,
        message: Optional[str] = None,
    ) -> StreamBadge:
        """Send a badge/donation to a stream"""
        return crud_stream_badge.create_badge(
            session,
            stream_id=stream_id,
            sender_id=sender_id,
            badge_type=badge_type,
            amount=amount,
            message=message,
        )

    @staticmethod
    def get_stream_badges(session: Session, stream_id: UUID) -> list[StreamBadge]:
        """Get all badges for a stream"""
        return crud_stream_badge.get_by_stream_id(session, stream_id=stream_id)

    @staticmethod
    def get_recent_badges(
        session: Session, stream_id: UUID, limit: int = 50
    ) -> list[StreamBadge]:
        """Get recent badges for a stream"""
        return crud_stream_badge.get_recent_badges(
            session, stream_id=stream_id, limit=limit
        )

    @staticmethod
    def get_user_badges(session: Session, sender_id: UUID) -> list[StreamBadge]:
        """Get all badges sent by a user"""
        return crud_stream_badge.get_by_sender_id(session, sender_id=sender_id)

    @staticmethod
    def get_badges_by_type(
        session: Session, stream_id: UUID, badge_type: str
    ) -> list[StreamBadge]:
        """Get badges of specific type for a stream"""
        return crud_stream_badge.get_badges_by_type(
            session, stream_id=stream_id, badge_type=badge_type
        )

    @staticmethod
    def get_badge(session: Session, badge_id: UUID) -> Optional[StreamBadge]:
        """Get badge by ID"""
        return crud_stream_badge.get(session, badge_id)

    @staticmethod
    def get_total_donations(session: Session, stream_id: UUID) -> float:
        """Get total donation amount for a stream"""
        return crud_stream_badge.get_total_donations(session, stream_id=stream_id)

    @staticmethod
    def get_top_donors(
        session: Session, stream_id: UUID, limit: int = 10
    ) -> list[dict]:
        """Get top donors for a stream"""
        return crud_stream_badge.get_top_donors(
            session, stream_id=stream_id, limit=limit
        )

    @staticmethod
    def get_badge_stats(session: Session, stream_id: UUID) -> dict:
        """Get comprehensive badge statistics for a stream"""
        return crud_stream_badge.get_badge_stats(session, stream_id=stream_id)

    @staticmethod
    def update_badge(
        session: Session, badge_id: UUID, update_data: dict
    ) -> Optional[StreamBadge]:
        """Update badge details (admin only)"""
        from app.modules.live_streams.schema.badge import StreamBadgeUpdate

        badge = crud_stream_badge.get(session, badge_id)
        if badge:
            update_obj = StreamBadgeUpdate(**update_data)
            return crud_stream_badge.update(session, db_obj=badge, obj_in=update_obj)
        return None

    @staticmethod
    def delete_badge(session: Session, badge_id: UUID) -> bool:
        """Delete a badge (admin only)"""
        badge = crud_stream_badge.get(session, badge_id)
        if badge:
            crud_stream_badge.remove(session, id=badge_id)
            return True
        return False

    @staticmethod
    def get_donation_leaderboard(
        session: Session, stream_id: UUID, timeframe: str = "all"
    ) -> list[dict]:
        """Get donation leaderboard for a stream"""
        # For now, return top donors
        # In a real implementation, this would filter by timeframe
        return crud_stream_badge.get_top_donors(session, stream_id=stream_id, limit=20)

    @staticmethod
    def process_donation(
        session: Session,
        stream_id: UUID,
        sender_id: UUID,
        amount: float,
        badge_type: str = "heart",
        message: Optional[str] = None,
    ) -> StreamBadge:
        """Process a donation with validation"""
        if amount <= 0:
            raise ValueError("Donation amount must be positive")

        # Create the badge/donation
        badge = crud_stream_badge.create_badge(
            session,
            stream_id=stream_id,
            sender_id=sender_id,
            badge_type=badge_type,
            amount=amount,
            message=message,
        )

        # Update stream donation total
        from app.modules.live_streams.services.stream_service import stream_service

        stream_service.increment_stream_analytics(
            session, stream_id, donations=amount, badges=1
        )

        return badge


stream_badge_service = StreamBadgeService()
