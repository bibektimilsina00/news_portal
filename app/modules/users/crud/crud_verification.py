import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlmodel import Session, select

from app.modules.users.model.verification import (
    VerificationBadge,
    VerificationRequest,
    VerificationStatus,
    VerificationType,
)
from app.modules.users.schema.verification import (
    VerificationRequestCreate,
    VerificationRequestUpdate,
)
from app.shared.crud.base import CRUDBase


class CRUDVerificationRequest(
    CRUDBase[VerificationRequest, VerificationRequestCreate, VerificationRequestUpdate]
):
    """CRUD operations for VerificationRequest model"""

    def get_by_user_id(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[VerificationRequest]:
        """Get verification request by user ID"""
        statement = select(VerificationRequest).where(
            VerificationRequest.user_id == user_id
        )
        return session.exec(statement).first()

    def get_pending_requests(
        self, session: Session, skip: int = 0, limit: int = 50
    ) -> List[VerificationRequest]:
        """Get all pending verification requests"""
        statement = (
            select(VerificationRequest)
            .where(VerificationRequest.status == VerificationStatus.PENDING)
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_requests_by_status(
        self,
        session: Session,
        *,
        status: VerificationStatus,
        skip: int = 0,
        limit: int = 50,
    ) -> List[VerificationRequest]:
        """Get verification requests by status"""
        statement = (
            select(VerificationRequest)
            .where(VerificationRequest.status == status)
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def approve_request(
        self,
        session: Session,
        *,
        request_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        notes: Optional[str] = None,
    ) -> Optional[VerificationRequest]:
        """Approve a verification request"""
        request = self.get(session=session, id=request_id)
        if request and request.status == VerificationStatus.PENDING:
            request.approve(reviewer_id, notes)
            session.commit()
            session.refresh(request)
            return request
        return None

    def reject_request(
        self,
        session: Session,
        *,
        request_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        reason: str,
        notes: Optional[str] = None,
    ) -> Optional[VerificationRequest]:
        """Reject a verification request"""
        request = self.get(session=session, id=request_id)
        if request and request.status == VerificationStatus.PENDING:
            request.reject(reviewer_id, reason, notes)
            session.commit()
            session.refresh(request)
            return request
        return None

    def mark_under_review(
        self, session: Session, *, request_id: uuid.UUID
    ) -> Optional[VerificationRequest]:
        """Mark request as under review"""
        request = self.get(session=session, id=request_id)
        if request and request.status == VerificationStatus.PENDING:
            request.mark_under_review()
            session.commit()
            session.refresh(request)
            return request
        return None

    def get_expired_requests(self, session: Session) -> List[VerificationRequest]:
        """Get all expired verification requests"""
        from datetime import datetime

        current_time = datetime.utcnow()

        statement = select(VerificationRequest).where(
            VerificationRequest.status == VerificationStatus.PENDING,
            VerificationRequest.submitted_at < (current_time - timedelta(days=30)),
        )
        return list(session.exec(statement))


class CRUDVerificationBadge:
    """CRUD operations for VerificationBadge model"""

    def get_by_user_id(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[VerificationBadge]:
        """Get active verification badge for user"""
        statement = select(VerificationBadge).where(
            VerificationBadge.user_id == user_id, VerificationBadge.is_active == True
        )
        return session.exec(statement).first()

    def get_all_user_badges(
        self, session: Session, *, user_id: uuid.UUID
    ) -> List[VerificationBadge]:
        """Get all verification badges for user (active and inactive)"""
        statement = select(VerificationBadge).where(
            VerificationBadge.user_id == user_id
        )
        return list(session.exec(statement))

    def create_badge(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        verification_request_id: uuid.UUID,
        badge_type: VerificationType,
        badge_name: str,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> VerificationBadge:
        """Create a new verification badge"""
        badge = VerificationBadge(
            user_id=user_id,
            verification_request_id=verification_request_id,
            badge_type=badge_type,
            badge_name=badge_name,
            description=description,
            expires_at=expires_at,
        )
        session.add(badge)
        session.commit()
        session.refresh(badge)
        return badge

    def deactivate_badge(
        self, session: Session, *, badge_id: uuid.UUID
    ) -> Optional[VerificationBadge]:
        """Deactivate a verification badge"""
        badge = session.get(VerificationBadge, badge_id)
        if badge:
            badge.deactivate()
            session.commit()
            session.refresh(badge)
            return badge
        return None

    def extend_badge_validity(
        self, session: Session, *, badge_id: uuid.UUID, days: int
    ) -> Optional[VerificationBadge]:
        """Extend badge validity"""
        badge = session.get(VerificationBadge, badge_id)
        if badge:
            badge.extend_validity(days)
            session.commit()
            session.refresh(badge)
            return badge
        return None

    def get_expiring_badges(
        self, session: Session, *, days_ahead: int = 30
    ) -> List[VerificationBadge]:
        """Get badges expiring within specified days"""
        from datetime import datetime, timedelta

        expiry_date = datetime.utcnow() + timedelta(days=days_ahead)

        statement = select(VerificationBadge).where(
            VerificationBadge.is_active == True,
            VerificationBadge.expires_at != None,
            VerificationBadge.expires_at <= expiry_date,
        )
        return list(session.exec(statement))


# Create singleton instances
verification_request = CRUDVerificationRequest(VerificationRequest)
verification_badge = CRUDVerificationBadge()
