import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import JSON, Column, Enum, Field, Relationship, SQLModel

from app.shared.enums import VerificationStatus, VerificationType

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class VerificationRequest(SQLModel, table=True):
    """Verification requests for journalists and organizations"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Request details
    verification_type: VerificationType
    status: VerificationStatus = Field(default=VerificationStatus.PENDING)

    # Personal/Organization information
    full_name: str = Field(max_length=255)
    category: str = Field(max_length=100)  # e.g., "Politics", "Technology", "Sports"
    description: Optional[str] = Field(default=None, max_length=1000)

    # Contact information
    contact_email: str = Field(max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)

    # Documentation
    identification_document_url: Optional[str] = Field(default=None, max_length=500)
    articles_of_incorporation_url: Optional[str] = Field(default=None, max_length=500)
    official_website_url: Optional[str] = Field(default=None, max_length=255)
    social_media_links: List[str] = Field(default=[], sa_column=Column(JSON))

    # Additional documents
    additional_documents: List[str] = Field(default=[], sa_column=Column(JSON))

    # Review process
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(default=None)
    reviewed_by: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    review_notes: Optional[str] = Field(default=None, max_length=2000)
    rejection_reason: Optional[str] = Field(default=None, max_length=500)

    # Verification badge
    badge_issued_at: Optional[datetime] = Field(default=None)
    badge_expires_at: Optional[datetime] = Field(default=None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="verification_requests")
    reviewer: Optional["User"] = Relationship(
        back_populates="reviewed_requests",
        sa_relationship_kwargs={"foreign_keys": "VerificationRequest.reviewed_by"},
    )

    class Config:
        from_attributes = True

    def is_expired(self) -> bool:
        """Check if verification request has expired"""
        # Requests expire after 30 days if not reviewed
        from datetime import timedelta

        return self.submitted_at + timedelta(days=30) < datetime.utcnow()

    def approve(self, reviewer_id: uuid.UUID, notes: Optional[str] = None) -> None:
        """Approve the verification request"""
        self.status = VerificationStatus.APPROVED
        self.reviewed_at = datetime.utcnow()
        self.reviewed_by = reviewer_id
        self.review_notes = notes
        self.badge_issued_at = datetime.utcnow()
        # Badge expires in 1 year
        from datetime import timedelta

        self.badge_expires_at = datetime.utcnow() + timedelta(days=365)
        self.updated_at = datetime.utcnow()

    def reject(
        self, reviewer_id: uuid.UUID, reason: str, notes: Optional[str] = None
    ) -> None:
        """Reject the verification request"""
        self.status = VerificationStatus.REJECTED
        self.reviewed_at = datetime.utcnow()
        self.reviewed_by = reviewer_id
        self.rejection_reason = reason
        self.review_notes = notes
        self.updated_at = datetime.utcnow()

    def mark_under_review(self) -> None:
        """Mark request as under review"""
        self.status = VerificationStatus.UNDER_REVIEW
        self.updated_at = datetime.utcnow()


class VerificationBadge(SQLModel, table=True):
    """Verification badges earned by users"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    verification_request_id: uuid.UUID = Field(foreign_key="verification_requests.id")

    # Badge details
    badge_type: VerificationType
    badge_name: str = Field(
        max_length=100
    )  # e.g., "Verified Journalist", "Verified Organization"
    description: Optional[str] = Field(default=None, max_length=500)

    # Validity
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="verification_badges")
    verification_request: VerificationRequest = Relationship(back_populates="badge")

    class Config:
        from_attributes = True

    def is_expired(self) -> bool:
        """Check if badge has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def deactivate(self) -> None:
        """Deactivate the badge"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def extend_validity(self, days: int) -> None:
        """Extend badge validity"""
        from datetime import timedelta

        if self.expires_at:
            self.expires_at = self.expires_at + timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        self.updated_at = datetime.utcnow()


# Update VerificationRequest to include badge relationship
# Note: Badge relationship is defined in VerificationBadge model
