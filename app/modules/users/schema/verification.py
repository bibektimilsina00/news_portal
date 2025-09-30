import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_validator
from sqlmodel import SQLModel


# Base Verification Schema
class VerificationBase(SQLModel):
    """Base verification schema"""

    verification_type: str = Field(
        ..., description="Type of verification: journalist, organization, business"
    )
    full_name: str = Field(..., max_length=255)
    category: str = Field(
        ..., max_length=100, description="Category like Politics, Technology, Sports"
    )
    description: Optional[str] = Field(default=None, max_length=1000)

    # Contact information
    contact_email: str = Field(..., max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)

    # Documentation
    identification_document_url: Optional[str] = Field(default=None, max_length=500)
    articles_of_incorporation_url: Optional[str] = Field(default=None, max_length=500)
    official_website_url: Optional[str] = Field(default=None, max_length=255)
    social_media_links: List[str] = Field(default=[])

    # Additional documents
    additional_documents: List[str] = Field(default=[])

    @field_validator("verification_type")
    @classmethod
    def validate_verification_type(cls, v):
        allowed_types = ["journalist", "organization", "business"]
        if v not in allowed_types:
            raise ValueError(
                f"Verification type must be one of: {', '.join(allowed_types)}"
            )
        return v

    @field_validator(
        "official_website_url",
        "identification_document_url",
        "articles_of_incorporation_url",
    )
    @classmethod
    def validate_document_urls(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Document URL must start with http:// or https://")
        return v

    @field_validator("social_media_links")
    @classmethod
    def validate_social_links(cls, v):
        if v:
            for url in v:
                if not url.startswith(("http://", "https://")):
                    raise ValueError(
                        "Social media links must start with http:// or https://"
                    )
        return v


# Create/Update Schemas
class VerificationRequestCreate(VerificationBase):
    """Schema for creating a verification request"""

    pass


class VerificationRequestUpdate(SQLModel):
    """Schema for updating a verification request"""

    full_name: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    contact_email: Optional[str] = Field(default=None, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    identification_document_url: Optional[str] = Field(default=None, max_length=500)
    articles_of_incorporation_url: Optional[str] = Field(default=None, max_length=500)
    official_website_url: Optional[str] = Field(default=None, max_length=255)
    social_media_links: Optional[List[str]] = None
    additional_documents: Optional[List[str]] = None


# Response Schemas
class VerificationRequestResponse(VerificationBase):
    """Schema for verification request response"""

    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[uuid.UUID] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    badge_issued_at: Optional[datetime] = None
    badge_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class VerificationBadgeResponse(SQLModel):
    """Schema for verification badge response"""

    id: uuid.UUID
    user_id: uuid.UUID
    verification_request_id: uuid.UUID
    badge_type: str
    badge_name: str
    description: Optional[str] = None
    issued_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool


# Admin Review Schemas
class VerificationReviewRequest(SQLModel):
    """Schema for admin to review verification requests"""

    action: str = Field(..., description="Action: approve, reject")
    review_notes: Optional[str] = Field(default=None, max_length=2000)
    rejection_reason: Optional[str] = Field(
        default=None, max_length=500, description="Required if action is reject"
    )

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        if v not in ["approve", "reject"]:
            raise ValueError("Action must be either 'approve' or 'reject'")
        return v

    @field_validator("rejection_reason")
    @classmethod
    def validate_rejection_reason(cls, v, info):
        if info.data and info.data.get("action") == "reject" and not v:
            raise ValueError("Rejection reason is required when rejecting a request")
        return v


class VerificationReviewResponse(SQLModel):
    """Schema for verification review response"""

    success: bool
    message: str
    request_id: uuid.UUID
    new_status: str
    badge_issued: Optional[bool] = None


# List Schemas
class VerificationRequestsList(SQLModel):
    """Schema for verification requests list"""

    requests: List[VerificationRequestResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class VerificationBadgesList(SQLModel):
    """Schema for verification badges list"""

    badges: List[VerificationBadgeResponse]
    total: int


# Statistics Schemas
class VerificationStats(SQLModel):
    """Verification statistics"""

    total_requests: int
    pending_requests: int
    approved_requests: int
    rejected_requests: int
    expired_requests: int
    active_badges: int
    badges_by_type: dict  # {"journalist": 10, "organization": 5, "business": 3}


class VerificationDashboard(SQLModel):
    """Verification dashboard for admins"""

    stats: VerificationStats
    recent_requests: List[VerificationRequestResponse]
    expiring_badges: List[VerificationBadgeResponse]


# Public Verification Schemas
class PublicVerificationInfo(SQLModel):
    """Public verification information for user profiles"""

    is_verified: bool
    verification_type: Optional[str] = None
    badge_name: Optional[str] = None
    verified_since: Optional[datetime] = None
    badge_expires_at: Optional[datetime] = None


# Appeal Schemas
class VerificationAppealRequest(SQLModel):
    """Schema for appealing a rejected verification"""

    appeal_reason: str = Field(
        ..., max_length=1000, description="Reason for appealing the rejection"
    )
    additional_documents: List[str] = Field(
        default=[], description="Additional documents to support appeal"
    )
    updated_information: Optional[dict] = Field(
        default=None, description="Updated information for the request"
    )

    @field_validator("appeal_reason")
    @classmethod
    def validate_appeal_reason(cls, v):
        if len(v.strip()) < 50:
            raise ValueError("Appeal reason must be at least 50 characters long")
        return v.strip()


class VerificationAppealResponse(SQLModel):
    """Schema for verification appeal response"""

    id: uuid.UUID
    original_request_id: uuid.UUID
    appeal_reason: str
    status: str  # pending, approved, rejected
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
