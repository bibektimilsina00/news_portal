import uuid
from datetime import datetime
from typing import List, Optional

from app.modules.users.crud.crud_verification import (
    verification_badge,
    verification_request,
)
from app.modules.users.model.verification import (
    VerificationBadge,
    VerificationRequest,
    VerificationStatus,
    VerificationType,
)
from app.modules.users.schema.verification import (
    VerificationAppealRequest,
    VerificationRequestCreate,
    VerificationReviewRequest,
)
from app.shared.deps.deps import SessionDep


class VerificationService:
    """Service layer for verification operations"""

    @staticmethod
    def create_verification_request(
        session: SessionDep,
        *,
        user_id: uuid.UUID,
        request_data: VerificationRequestCreate,
    ) -> VerificationRequest:
        """Create a new verification request"""
        # Check if user already has a pending request
        existing_request = verification_request.get_by_user_id(
            session=session, user_id=user_id
        )
        if existing_request and existing_request.status == VerificationStatus.pending:
            raise ValueError("User already has a pending verification request")

        # Create the request
        request_dict = request_data.model_dump()
        request_dict["user_id"] = user_id
        db_obj = VerificationRequest(**request_dict)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_user_verification_request(
        session: SessionDep, *, user_id: uuid.UUID
    ) -> Optional[VerificationRequest]:
        """Get verification request for a user"""
        return verification_request.get_by_user_id(session=session, user_id=user_id)

    @staticmethod
    def get_pending_requests(
        session: SessionDep, *, skip: int = 0, limit: int = 50
    ) -> List[VerificationRequest]:
        """Get all pending verification requests (admin only)"""
        return verification_request.get_pending_requests(
            session=session, skip=skip, limit=limit
        )

    @staticmethod
    def review_verification_request(
        session: SessionDep,
        *,
        request_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        review_data: VerificationReviewRequest,
    ) -> Optional[VerificationRequest]:
        """Review a verification request (approve or reject)"""
        if review_data.action == "approve":
            return verification_request.approve_request(
                session=session,
                request_id=request_id,
                reviewer_id=reviewer_id,
                notes=review_data.review_notes,
            )
        elif review_data.action == "reject":
            if not review_data.rejection_reason:
                raise ValueError("Rejection reason is required")
            return verification_request.reject_request(
                session=session,
                request_id=request_id,
                reviewer_id=reviewer_id,
                reason=review_data.rejection_reason,
                notes=review_data.review_notes,
            )
        else:
            raise ValueError("Invalid review action")

    @staticmethod
    def mark_request_under_review(
        session: SessionDep, *, request_id: uuid.UUID
    ) -> Optional[VerificationRequest]:
        """Mark a request as under review"""
        return verification_request.mark_under_review(
            session=session, request_id=request_id
        )

    @staticmethod
    def get_user_verification_badge(
        session: SessionDep, *, user_id: uuid.UUID
    ) -> Optional[VerificationBadge]:
        """Get active verification badge for a user"""
        return verification_badge.get_by_user_id(session=session, user_id=user_id)

    @staticmethod
    def get_user_verification_history(
        session: SessionDep, *, user_id: uuid.UUID
    ) -> List[VerificationBadge]:
        """Get all verification badges for a user"""
        return verification_badge.get_all_user_badges(session=session, user_id=user_id)

    @staticmethod
    def create_verification_badge(
        session: SessionDep,
        *,
        user_id: uuid.UUID,
        verification_request_id: uuid.UUID,
        badge_type: VerificationType,
        badge_name: str,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> VerificationBadge:
        """Create a verification badge (called after request approval)"""
        return verification_badge.create_badge(
            session=session,
            user_id=user_id,
            verification_request_id=verification_request_id,
            badge_type=badge_type,
            badge_name=badge_name,
            description=description,
            expires_at=expires_at,
        )

    @staticmethod
    def deactivate_verification_badge(
        session: SessionDep, *, badge_id: uuid.UUID
    ) -> Optional[VerificationBadge]:
        """Deactivate a verification badge"""
        return verification_badge.deactivate_badge(session=session, badge_id=badge_id)

    @staticmethod
    def extend_badge_validity(
        session: SessionDep, *, badge_id: uuid.UUID, days: int
    ) -> Optional[VerificationBadge]:
        """Extend badge validity"""
        return verification_badge.extend_badge_validity(
            session=session, badge_id=badge_id, days=days
        )

    @staticmethod
    def get_expiring_badges(
        session: SessionDep, *, days_ahead: int = 30
    ) -> List[VerificationBadge]:
        """Get badges expiring soon (for notifications)"""
        return verification_badge.get_expiring_badges(
            session=session, days_ahead=days_ahead
        )

    @staticmethod
    def appeal_verification_rejection(
        session: SessionDep,
        *,
        user_id: uuid.UUID,
        appeal_data: VerificationAppealRequest,
    ) -> VerificationRequest:
        """Create an appeal for a rejected verification request"""
        # Get the rejected request
        existing_request = verification_request.get_by_user_id(
            session=session, user_id=user_id
        )
        if (
            not existing_request
            or existing_request.status != VerificationStatus.REJECTED
        ):
            raise ValueError("No rejected verification request found to appeal")

        # Create a new request with appeal information
        appeal_request_data = VerificationRequestCreate(
            verification_type=existing_request.verification_type,
            full_name=existing_request.full_name,
            category=existing_request.category,
            description=appeal_data.appeal_reason,
            contact_email=existing_request.contact_email,
            phone_number=existing_request.phone_number,
            identification_document_url=existing_request.identification_document_url,
            articles_of_incorporation_url=existing_request.articles_of_incorporation_url,
            official_website_url=existing_request.official_website_url,
            additional_documents=appeal_data.additional_documents,
        )

        return VerificationService.create_verification_request(
            session=session, user_id=user_id, request_data=appeal_request_data
        )


# Create service instance
verification_service = VerificationService()
