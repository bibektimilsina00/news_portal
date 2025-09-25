from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.modules.live_streams.model.badge import StreamBadge
from app.modules.live_streams.schema.badge import StreamBadgeCreate, StreamBadgeUpdate
from app.shared.crud.base import CRUDBase


class CRUDStreamBadge(CRUDBase[StreamBadge, StreamBadgeCreate, StreamBadgeUpdate]):
    """CRUD operations for stream badges"""

    def get_by_stream_id(self, session: Session, stream_id: UUID) -> list[StreamBadge]:
        """Get all badges for a stream"""
        return list(
            session.exec(
                select(StreamBadge).where(StreamBadge.stream_id == stream_id)
            ).all()
        )

    def get_by_sender_id(self, session: Session, sender_id: UUID) -> list[StreamBadge]:
        """Get all badges sent by a user"""
        return list(
            session.exec(
                select(StreamBadge).where(StreamBadge.sender_id == sender_id)
            ).all()
        )

    def get_recent_badges(
        self, session: Session, stream_id: UUID, limit: int = 50
    ) -> list[StreamBadge]:
        """Get recent badges for a stream"""
        return list(
            session.exec(
                select(StreamBadge)
                .where(StreamBadge.stream_id == stream_id)
                .order_by(StreamBadge.sent_at.desc())
                .limit(limit)
            ).all()
        )

    def get_badges_by_type(
        self, session: Session, stream_id: UUID, badge_type: str
    ) -> list[StreamBadge]:
        """Get badges of specific type for a stream"""
        return list(
            session.exec(
                select(StreamBadge).where(
                    StreamBadge.stream_id == stream_id,
                    StreamBadge.badge_type == badge_type,
                )
            ).all()
        )

    def get_total_donations(self, session: Session, stream_id: UUID) -> float:
        """Get total donation amount for a stream"""
        result = session.exec(
            select(StreamBadge.amount).where(StreamBadge.stream_id == stream_id)
        ).all()
        return sum(amount for amount in result if amount > 0)

    def get_top_donors(
        self, session: Session, stream_id: UUID, limit: int = 10
    ) -> list[dict]:
        """Get top donors for a stream"""
        # This would require more complex aggregation, simplified for now
        badges = self.get_by_stream_id(session, stream_id)
        donor_totals = {}

        for badge in badges:
            if badge.amount > 0:
                sender_id = str(badge.sender_id)
                donor_totals[sender_id] = donor_totals.get(sender_id, 0) + badge.amount

        # Sort by total amount
        sorted_donors = sorted(donor_totals.items(), key=lambda x: x[1], reverse=True)
        return [
            {"sender_id": UUID(sender_id), "total_amount": amount}
            for sender_id, amount in sorted_donors[:limit]
        ]

    def create_badge(
        self,
        session: Session,
        stream_id: UUID,
        sender_id: UUID,
        badge_type: str,
        amount: float,
        message: Optional[str] = None,
    ) -> StreamBadge:
        """Create a new badge/donation"""
        from app.modules.live_streams.model.badge import BadgeType

        badge_data = StreamBadgeCreate(
            stream_id=stream_id,
            sender_id=sender_id,
            badge_type=BadgeType(badge_type),
            amount=amount,
            message=message,
            sent_at=datetime.utcnow(),
        )
        return self.create(session, obj_in=badge_data)

    def get_badge_stats(self, session: Session, stream_id: UUID) -> dict:
        """Get badge statistics for a stream"""
        badges = self.get_by_stream_id(session, stream_id)

        stats = {
            "total_badges": len(badges),
            "total_amount": sum(badge.amount for badge in badges),
            "badge_types": {},
            "hourly_distribution": {},
        }

        for badge in badges:
            # Count by type
            badge_type = (
                badge.badge_type.value
                if hasattr(badge.badge_type, "value")
                else str(badge.badge_type)
            )
            stats["badge_types"][badge_type] = (
                stats["badge_types"].get(badge_type, 0) + 1
            )

            # Hourly distribution
            hour = badge.sent_at.hour
            stats["hourly_distribution"][str(hour)] = (
                stats["hourly_distribution"].get(str(hour), 0) + 1
            )

        return stats


crud_stream_badge = CRUDStreamBadge(StreamBadge)
