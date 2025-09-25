import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Enum, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.news.model.news import News
    from app.modules.users.model.user import User


class FactCheckStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FALSE = "false"
    MISLEADING = "misleading"
    PARTIALLY_TRUE = "partially_true"
    UNVERIFIABLE = "unverifiable"


class FactCheckPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class FactCheck(SQLModel, table=True):
    """Fact checking for news articles"""

    __tablename__ = "fact_checks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    news_id: uuid.UUID = Field(foreign_key="news.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)  # Fact checker
    organization_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.id"
    )  # Organization

    # Fact Check Details
    status: FactCheckStatus = Field(default=FactCheckStatus.PENDING, index=True)
    priority: FactCheckPriority = Field(default=FactCheckPriority.MEDIUM)

    # Claims being checked
    claim_summary: str = Field(sa_column_kwargs={"type_": "TEXT"})
    claim_text: str = Field(sa_column_kwargs={"type_": "TEXT"})
    claim_context: Optional[str] = Field(
        default=None, sa_column_kwargs={"type_": "TEXT"}
    )

    # Fact Check Results
    verdict: Optional[str] = Field(default=None, max_length=255)
    verdict_summary: Optional[str] = Field(
        default=None, sa_column_kwargs={"type_": "TEXT"}
    )
    detailed_analysis: Optional[str] = Field(
        default=None, sa_column_kwargs={"type_": "TEXT"}
    )

    # Evidence & Sources
    evidence_summary: Optional[str] = Field(
        default=None, sa_column_kwargs={"type_": "TEXT"}
    )
    evidence_links: List[str] = Field(default=[], sa_column_kwargs={"type_": "JSON"})
    source_reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Verification Process
    verification_method: str = Field(
        default="manual", max_length=50
    )  # manual, automated, mixed
    verification_tools: List[str] = Field(
        default=[], sa_column_kwargs={"type_": "JSON"}
    )
    verification_criteria: Optional[str] = Field(
        default=None, sa_column_kwargs={"type_": "TEXT"}
    )

    # Confidence & Reliability
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reliability_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    evidence_strength: Optional[str] = Field(
        default=None, max_length=50
    )  # weak, moderate, strong, very_strong

    # Cross-References
    related_fact_checks: List[uuid.UUID] = Field(
        default=[], sa_column_kwargs={"type_": "JSON"}
    )
    contradicting_fact_checks: List[uuid.UUID] = Field(
        default=[], sa_column_kwargs={"type_": "JSON"}
    )

    # External References
    external_fact_check_urls: List[str] = Field(
        default=[], sa_column_kwargs={"type_": "JSON"}
    )
    fact_check_organizations: List[str] = Field(
        default=[], sa_column_kwargs={"type_": "JSON"}
    )

    # Media & Attachments
    supporting_documents: List[str] = Field(
        default=[], sa_column_kwargs={"type_": "JSON"}
    )
    evidence_images: List[str] = Field(default=[], sa_column_kwargs={"type_": "JSON"})
    verification_videos: List[str] = Field(
        default=[], sa_column_kwargs={"type_": "JSON"}
    )

    # Status & Workflow
    assigned_at: Optional[datetime] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    reviewed_at: Optional[datetime] = Field(default=None)

    # Review Process
    review_status: str = Field(
        default="pending", max_length=50
    )  # pending, under_review, approved, rejected
    review_notes: Optional[str] = Field(
        default=None, sa_column_kwargs={"type_": "TEXT"}
    )
    reviewed_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

    # Public Visibility
    is_public: bool = Field(default=True)
    public_notes: Optional[str] = Field(
        default=None, sa_column_kwargs={"type_": "TEXT"}
    )

    # Legal & Compliance
    legal_notes: Optional[str] = Field(default=None, sa_column_kwargs={"type_": "TEXT"})
    compliance_status: str = Field(
        default="pending", max_length=50
    )  # pending, compliant, non_compliant
    jurisdiction: Optional[str] = Field(default=None, max_length=100)

    # Impact & Metrics
    impact_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    public_interest_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    media_mentions: int = Field(default=0)

    # Engagement
    view_count: int = Field(default=0)
    share_count: int = Field(default=0)
    helpful_votes: int = Field(default=0)
    not_helpful_votes: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    news: "News" = Relationship(back_populates="fact_checks")
    checker: "User" = Relationship(back_populates="fact_checks")
    organization: Optional["User"] = Relationship(
        back_populates="organization_fact_checks"
    )

    class Config:
        orm_mode = True

    def mark_as_started(self) -> None:
        """Mark fact check as started"""
        self.started_at = datetime.utcnow()
        if self.status == FactCheckStatus.PENDING:
            self.status = FactCheckStatus.UNDER_REVIEW

    def mark_as_completed(self, status: FactCheckStatus) -> None:
        """Mark fact check as completed"""
        self.completed_at = datetime.utcnow()
        self.status = status

    def increment_view_count(self) -> None:
        """Increment view count"""
        self.view_count += 1

    def increment_share_count(self) -> None:
        """Increment share count"""
        self.share_count += 1

    def add_helpful_vote(self) -> None:
        """Add helpful vote"""
        self.helpful_votes += 1

    def add_not_helpful_vote(self) -> None:
        """Add not helpful vote"""
        self.not_helpful_votes += 1

    def get_credibility_rating(self) -> str:
        """Get credibility rating based on scores"""
        if self.confidence_score is None:
            return "unknown"
        elif self.confidence_score >= 0.9:
            return "very_high"
        elif self.confidence_score >= 0.8:
            return "high"
        elif self.confidence_score >= 0.6:
            return "moderate"
        elif self.confidence_score >= 0.4:
            return "low"
        else:
            return "very_low"


class FactCheckVote(SQLModel, table=True):
    """User votes on fact checks"""

    __tablename__ = "fact_check_votes"

    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    fact_check_id: uuid.UUID = Field(foreign_key="fact_checks.id", primary_key=True)
    is_helpful: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class FactCheckComment(SQLModel, table=True):
    """Comments on fact checks"""

    __tablename__ = "fact_check_comments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    fact_check_id: uuid.UUID = Field(foreign_key="fact_checks.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    parent_comment_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="fact_check_comments.id"
    )

    content: str = Field(sa_column_kwargs={"type_": "TEXT"})
    is_public: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        orm_mode = True
