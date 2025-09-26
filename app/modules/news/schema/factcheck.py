import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.modules.news.model.factcheck import FactCheckPriority, FactCheckStatus


# Base Schemas
class FactCheckBase(SQLModel):
    """Base fact check schema"""

    claim_summary: str = Field(max_length=1000)
    claim_details: Optional[str] = Field(default=None)
    claim_context: Optional[str] = Field(default=None)

    # Verification results
    verdict: Optional[str] = Field(default=None, max_length=1000)
    verdict_summary: Optional[str] = Field(default=None, max_length=500)
    detailed_analysis: Optional[str] = Field(default=None)

    # Evidence & sources
    evidence_summary: Optional[str] = Field(default=None)
    evidence_links: Optional[List[str]] = Field(default=None)
    evidence_documents: Optional[List[str]] = Field(default=None)
    verification_sources: Optional[List[str]] = Field(default=None)
    expert_quotes: Optional[str] = Field(default=None)

    # Confidence & reliability
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fact_checking_method: Optional[str] = Field(default=None, max_length=500)
    verification_process: Optional[str] = Field(default=None)

    # Cross-references
    related_fact_checks: Optional[List[uuid.UUID]] = Field(default=None)
    contradicting_fact_checks: Optional[List[uuid.UUID]] = Field(default=None)

    # Visual evidence
    fact_check_images: Optional[List[str]] = Field(default=None)
    fact_check_videos: Optional[List[str]] = Field(default=None)


class FactCheckCreate(FactCheckBase):
    """Create fact check schema"""

    news_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None

    status: FactCheckStatus = FactCheckStatus.PENDING
    priority: FactCheckPriority = FactCheckPriority.MEDIUM


class FactCheckUpdate(BaseModel):
    """Update fact check schema"""

    status: Optional[FactCheckStatus] = None
    priority: Optional[FactCheckPriority] = None

    claim_summary: Optional[str] = None
    claim_details: Optional[str] = None
    claim_context: Optional[str] = None

    verdict: Optional[str] = None
    verdict_summary: Optional[str] = None
    detailed_analysis: Optional[str] = None

    evidence_summary: Optional[str] = None
    evidence_links: Optional[List[str]] = None
    evidence_documents: Optional[List[str]] = None
    verification_sources: Optional[List[str]] = None
    expert_quotes: Optional[str] = None

    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fact_checking_method: Optional[str] = None
    verification_process: Optional[str] = None

    related_fact_checks: Optional[List[uuid.UUID]] = None
    contradicting_fact_checks: Optional[List[uuid.UUID]] = None

    fact_check_images: Optional[List[str]] = None
    fact_check_videos: Optional[List[str]] = None

    reviewed_by: Optional[List[uuid.UUID]] = None
    review_notes: Optional[str] = None


class FactCheckResponse(FactCheckBase):
    """Fact check response schema"""

    id: uuid.UUID
    news_id: uuid.UUID
    user_id: uuid.UUID
    organization_id: Optional[uuid.UUID]

    status: FactCheckStatus
    priority: FactCheckPriority

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class FactCheckListResponse(BaseModel):
    """Fact check list response"""

    fact_checks: List[FactCheckResponse]
    total: int
    page: int
    per_page: int


class FactCheckFilter(BaseModel):
    """Fact check filter schema"""

    status: Optional[FactCheckStatus] = None
    priority: Optional[FactCheckPriority] = None
    user_id: Optional[uuid.UUID] = None
    news_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None

    # Date range
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

    # Score range
    min_confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Search
    search_query: Optional[str] = None


class FactCheckVoteCreate(BaseModel):
    """Create fact check vote"""

    fact_check_id: uuid.UUID
    is_helpful: bool


class FactCheckVoteResponse(BaseModel):
    """Fact check vote response"""

    fact_check_id: uuid.UUID
    user_id: uuid.UUID
    is_helpful: bool
    created_at: datetime


class FactCheckCommentCreate(BaseModel):
    """Create fact check comment"""

    fact_check_id: uuid.UUID
    content: str
    parent_comment_id: Optional[uuid.UUID] = None
    is_public: bool = True


class FactCheckCommentResponse(BaseModel):
    """Fact check comment response"""

    id: uuid.UUID
    fact_check_id: uuid.UUID
    user_id: uuid.UUID
    parent_comment_id: Optional[uuid.UUID]
    content: str
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]


class FactCheckStats(BaseModel):
    """Fact check statistics"""

    total_fact_checks: int
    by_status: Dict[FactCheckStatus, int]
    by_priority: Dict[FactCheckPriority, int]
    average_confidence_score: Optional[float]
    average_reliability_score: Optional[float]


class FactCheckVerificationRequest(BaseModel):
    """Request fact check verification"""

    news_id: uuid.UUID
    claim_summary: str
    claim_details: Optional[str] = None
    priority: FactCheckPriority = FactCheckPriority.MEDIUM
    notes: Optional[str] = None


class FactCheckVerificationResponse(BaseModel):
    """Fact check verification response"""

    message: str
    fact_check_id: uuid.UUID
    status: FactCheckStatus


class ExternalFactCheckSubmission(BaseModel):
    """External fact check submission"""

    url: str
    claim_text: str
    verdict: str
    source: str
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
