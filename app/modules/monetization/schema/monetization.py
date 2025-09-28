from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import SQLModel


# Base schemas
class SubscriptionTierBase(SQLModel):
    name: str = Field(max_length=100)
    description: Optional[str] = None
    price_monthly: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    price_yearly: Optional[Decimal] = Field(
        max_digits=10, decimal_places=2, gt=0, default=None
    )
    features: List[str] = Field(default_factory=list)
    max_subscribers: Optional[int] = Field(default=None)


class UserSubscriptionBase(SQLModel):
    tier_id: UUID
    status: str = Field(default="active")
    cancel_at_period_end: bool = Field(default=False)


class PaymentBase(SQLModel):
    amount: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    currency: str = Field(max_length=3, default="USD")
    payment_method: str = Field(max_length=50)
    description: Optional[str] = None


class AdCampaignBase(SQLModel):
    name: str = Field(max_length=200)
    description: Optional[str] = None
    budget: Decimal = Field(max_digits=12, decimal_places=2, gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[dict] = Field(default_factory=dict)
    ad_content: dict = Field(default_factory=dict)


class CreatorEarningBase(SQLModel):
    source_type: str
    source_id: Optional[UUID] = None
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str = Field(max_length=3, default="USD")


class CreatorPayoutBase(SQLModel):
    amount: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    currency: str = Field(max_length=3, default="USD")
    payout_method: str = Field(max_length=50)


class SponsoredContentBase(SQLModel):
    brand_id: UUID
    content_id: UUID
    content_type: str
    compensation: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    currency: str = Field(max_length=3, default="USD")
    contract_details: Optional[dict] = Field(default_factory=dict)
    requirements: Optional[dict] = Field(default_factory=dict)


class PremiumFeatureBase(SQLModel):
    name: str = Field(max_length=100)
    description: str
    price: Decimal = Field(max_digits=8, decimal_places=2, gt=0)
    currency: str = Field(max_length=3, default="USD")
    feature_type: str
    extra_data: Optional[dict] = Field(default_factory=dict)


# Public schemas
class SubscriptionTierPublic(SubscriptionTierBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    creator_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserSubscriptionPublic(UserSubscriptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    tier: Optional[SubscriptionTierPublic] = None


class PaymentPublic(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    subscription_id: Optional[UUID] = None
    status: str
    payment_id: str
    created_at: datetime
    updated_at: datetime


class AdCampaignPublic(AdCampaignBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    advertiser_id: UUID
    spent: Decimal
    status: str
    created_at: datetime
    updated_at: datetime


class CreatorEarningPublic(CreatorEarningBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    creator_id: UUID
    status: str
    payout_id: Optional[UUID] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CreatorPayoutPublic(CreatorPayoutBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    creator_id: UUID
    status: str
    payout_id: Optional[str] = None
    period_start: datetime
    period_end: datetime
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class SponsoredContentPublic(SponsoredContentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    creator_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime


class PremiumFeaturePublic(PremiumFeatureBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PremiumFeaturePurchasePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    feature_id: UUID
    status: str
    expires_at: Optional[datetime] = None
    usage_count: int
    usage_limit: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    feature: Optional[PremiumFeaturePublic] = None


# Create schemas
class SubscriptionTierCreate(SubscriptionTierBase):
    pass


class UserSubscriptionCreate(BaseModel):
    tier_id: UUID
    payment_method: str = Field(max_length=50)


class PaymentCreate(PaymentBase):
    subscription_id: Optional[UUID] = None


class AdCampaignCreate(AdCampaignBase):
    pass


class CreatorEarningCreate(CreatorEarningBase):
    pass


class CreatorPayoutCreate(BaseModel):
    period_start: datetime
    period_end: datetime


class SponsoredContentCreate(SponsoredContentBase):
    pass


class PremiumFeatureCreate(PremiumFeatureBase):
    pass


class PremiumFeaturePurchaseCreate(BaseModel):
    feature_id: UUID
    payment_method: str = Field(max_length=50)


# Update schemas
class SubscriptionTierUpdate(BaseModel):
    name: Optional[str] = Field(max_length=100, default=None)
    description: Optional[str] = None
    price_monthly: Optional[Decimal] = Field(
        max_digits=10, decimal_places=2, gt=0, default=None
    )
    price_yearly: Optional[Decimal] = Field(
        max_digits=10, decimal_places=2, gt=0, default=None
    )
    features: Optional[List[str]] = None
    max_subscribers: Optional[int] = None
    is_active: Optional[bool] = None


class UserSubscriptionUpdate(BaseModel):
    status: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None


class PaymentUpdate(BaseModel):
    status: Optional[str] = None


class AdCampaignUpdate(BaseModel):
    name: Optional[str] = Field(max_length=200, default=None)
    description: Optional[str] = None
    budget: Optional[Decimal] = Field(
        max_digits=12, decimal_places=2, gt=0, default=None
    )
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[dict] = None
    ad_content: Optional[dict] = None


class CreatorEarningUpdate(BaseModel):
    status: Optional[str] = None
    payout_id: Optional[UUID] = None


class CreatorPayoutUpdate(BaseModel):
    status: Optional[str] = None
    payout_id: Optional[str] = None
    processed_at: Optional[datetime] = None


class SponsoredContentUpdate(BaseModel):
    status: Optional[str] = None
    compensation: Optional[Decimal] = Field(
        max_digits=10, decimal_places=2, gt=0, default=None
    )
    contract_details: Optional[dict] = None
    requirements: Optional[dict] = None


class PremiumFeatureUpdate(BaseModel):
    name: Optional[str] = Field(max_length=100, default=None)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(max_digits=8, decimal_places=2, gt=0, default=None)
    feature_type: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[dict] = None


class PremiumFeaturePurchaseUpdate(BaseModel):
    status: Optional[str] = None
    expires_at: Optional[datetime] = None
    usage_count: Optional[int] = None


# List schemas
class SubscriptionTierList(BaseModel):
    data: List[SubscriptionTierPublic]
    count: int


class UserSubscriptionList(BaseModel):
    data: List[UserSubscriptionPublic]
    count: int


class PaymentList(BaseModel):
    data: List[PaymentPublic]
    count: int


class AdCampaignList(BaseModel):
    data: List[AdCampaignPublic]
    count: int


class CreatorEarningList(BaseModel):
    data: List[CreatorEarningPublic]
    count: int


class CreatorPayoutList(BaseModel):
    data: List[CreatorPayoutPublic]
    count: int


class SponsoredContentList(BaseModel):
    data: List[SponsoredContentPublic]
    count: int


class PremiumFeatureList(BaseModel):
    data: List[PremiumFeaturePublic]
    count: int


class PremiumFeaturePurchaseList(BaseModel):
    data: List[PremiumFeaturePurchasePublic]
    count: int


# Additional schemas for specific operations
class SubscriptionCheckout(BaseModel):
    tier_id: UUID
    payment_method: str = Field(max_length=50)
    billing_cycle: str = Field(default="monthly")  # monthly, yearly


class AdImpressionCreate(BaseModel):
    campaign_id: UUID
    content_id: Optional[UUID] = None
    content_type: Optional[str] = None
    impression_type: str = Field(default="view")


class RevenueAnalytics(BaseModel):
    total_earnings: Decimal
    monthly_earnings: Decimal
    subscription_revenue: Decimal
    ad_revenue: Decimal
    sponsored_revenue: Decimal
    period_start: datetime
    period_end: datetime


class CreatorDashboard(BaseModel):
    total_subscribers: int
    monthly_revenue: Decimal
    total_earnings: Decimal
    pending_payouts: Decimal
    active_campaigns: int
    sponsored_posts: int
