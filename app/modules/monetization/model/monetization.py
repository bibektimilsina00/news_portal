from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.users.model.user import User


class SubscriptionTier(SQLModel, table=True):
    """Subscription tiers/plans for creators."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    creator_id: UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(max_length=100)
    description: Optional[str] = None
    price_monthly: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    price_yearly: Optional[Decimal] = Field(
        max_digits=10, decimal_places=2, gt=0, default=None
    )
    features: List[str] = Field(
        default_factory=list, sa_column=Column(JSON)
    )  # JSON array of features
    is_active: bool = Field(default=True)
    max_subscribers: Optional[int] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    creator: Optional["User"] = Relationship(back_populates="subscription_tiers")
    subscriptions: List["UserSubscription"] = Relationship(back_populates="tier")


class UserSubscription(SQLModel, table=True):
    """User subscriptions to creator tiers."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    tier_id: UUID = Field(foreign_key="subscriptiontier.id", index=True)
    status: str = Field(default="active")  # active, cancelled, expired, suspended
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = Field(default=False)
    cancelled_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="subscriptions")
    tier: Optional["SubscriptionTier"] = Relationship(back_populates="subscriptions")
    payments: List["Payment"] = Relationship(back_populates="subscription")


class Payment(SQLModel, table=True):
    """Payment transactions for subscriptions and purchases."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    subscription_id: Optional[UUID] = Field(
        default=None, foreign_key="usersubscription.id", index=True
    )
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    status: str = Field(default="pending")  # pending, completed, failed, refunded
    payment_method: str = Field(max_length=50)  # stripe, paypal, etc.
    payment_id: str = Field(unique=True, index=True)  # External payment provider ID
    description: Optional[str] = Field(default=None, max_length=255)
    extra_data: Optional[dict] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )  # JSON metadata

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="payments")
    subscription: Optional["UserSubscription"] = Relationship(back_populates="payments")


class AdCampaign(SQLModel, table=True):
    """Advertising campaigns for monetization."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    advertiser_id: UUID = Field(foreign_key="user.id", index=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    budget: Decimal = Field(max_digits=12, decimal_places=2)
    spent: Decimal = Field(default=0, max_digits=12, decimal_places=2)
    status: str = Field(default="draft")  # draft, active, paused, completed, cancelled
    target_audience: Optional[dict] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )  # JSON targeting criteria
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    impressions: int = Field(default=0)
    clicks: int = Field(default=0)
    conversions: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    advertiser: Optional["User"] = Relationship(back_populates="ad_campaigns")
    impressions_list: List["AdImpression"] = Relationship(
        back_populates="campaign", cascade_delete=True
    )


class AdImpression(SQLModel, table=True):
    """Individual ad impressions for tracking."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    campaign_id: UUID = Field(foreign_key="adcampaign.id", index=True)
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", index=True)
    impression_type: str = Field(default="view")  # view, click, conversion
    cost: Decimal = Field(max_digits=8, decimal_places=4)  # Cost per impression
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    campaign: Optional["AdCampaign"] = Relationship(back_populates="impressions_list")
    user: Optional["User"] = Relationship(back_populates="ad_impressions")


class CreatorEarning(SQLModel, table=True):
    """Creator earnings from various sources."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    creator_id: UUID = Field(foreign_key="user.id", index=True)
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    source_type: str = Field(
        max_length=50
    )  # subscription, ad_revenue, sponsored_content, etc.
    source_id: Optional[UUID] = Field(
        default=None
    )  # Reference to source (subscription, campaign, etc.)
    status: str = Field(default="pending")  # pending, available, paid, cancelled
    payout_id: Optional[UUID] = Field(default=None, foreign_key="creatorpayout.id")
    description: Optional[str] = Field(default=None, max_length=255)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    creator: Optional["User"] = Relationship(back_populates="earnings")
    payout: Optional["CreatorPayout"] = Relationship(back_populates="earnings")


class CreatorPayout(SQLModel, table=True):
    """Creator payout records."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    creator_id: UUID = Field(foreign_key="user.id", index=True)
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str = Field(default="USD", max_length=3)
    status: str = Field(default="pending")  # pending, processing, completed, failed
    payout_method: str = Field(max_length=50)  # bank_transfer, paypal, stripe, etc.
    payout_id: str = Field(unique=True, index=True)  # External payout provider ID
    fee: Decimal = Field(default=0, max_digits=8, decimal_places=2)  # Platform fee
    net_amount: Decimal = Field(max_digits=10, decimal_places=2)  # Amount after fees

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    processed_at: Optional[datetime] = None

    # Relationships
    creator: Optional["User"] = Relationship(back_populates="payouts")
    earnings: List["CreatorEarning"] = Relationship(
        back_populates="payout", cascade_delete=True
    )


class SponsoredContent(SQLModel, table=True):
    """Sponsored content tracking."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    creator_id: UUID = Field(foreign_key="user.id", index=True)
    brand_id: UUID = Field(foreign_key="user.id", index=True)
    content_id: UUID = Field(index=True)  # Post/story/reel ID
    content_type: str = Field()  # post, story, reel
    compensation: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    currency: str = Field(max_length=3, default="USD")
    status: str = Field(default="active")  # active, completed, cancelled
    contract_details: Optional[dict] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )  # JSON contract info
    requirements: Optional[dict] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )  # JSON requirements

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    creator: Optional["User"] = Relationship(back_populates="sponsored_content")
    brand: Optional["User"] = Relationship(back_populates="brand_sponsorships")


class PremiumFeature(SQLModel, table=True):
    """Premium features available for purchase."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str
    price: Decimal = Field(max_digits=8, decimal_places=2, gt=0)
    currency: str = Field(max_length=3, default="USD")
    feature_type: str = Field()  # boost, analytics, tools, etc.
    is_active: bool = Field(default=True)
    extra_data: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    purchases: List["PremiumFeaturePurchase"] = Relationship(back_populates="feature")


class PremiumFeaturePurchase(SQLModel, table=True):
    """User purchases of premium features."""

    id: UUID = Field(default_factory=UUID, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    feature_id: UUID = Field(foreign_key="premiumfeature.id", index=True)
    payment_id: Optional[UUID] = Field(foreign_key="payment.id", default=None)
    status: str = Field(default="active")  # active, expired, cancelled
    expires_at: Optional[datetime] = None
    usage_count: int = Field(default=0)
    usage_limit: Optional[int] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="premium_purchases")
    feature: Optional["PremiumFeature"] = Relationship(back_populates="purchases")
    payment: Optional["Payment"] = Relationship(back_populates="premium_purchase")
