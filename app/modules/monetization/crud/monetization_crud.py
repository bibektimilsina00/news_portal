from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, col, desc, func, select

from app.modules.monetization.model.monetization import (
    AdCampaign,
    AdImpression,
    CreatorEarning,
    CreatorPayout,
    Payment,
    PremiumFeature,
    PremiumFeaturePurchase,
    SponsoredContent,
    SubscriptionTier,
    UserSubscription,
)
from app.shared.crud.base import CRUDBase


class CRUDSubscriptionTier(
    CRUDBase[SubscriptionTier, SubscriptionTier, SubscriptionTier]
):
    """CRUD operations for subscription tiers."""

    def get_by_creator(
        self, session: Session, *, creator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[SubscriptionTier]:
        """Get subscription tiers by creator."""
        return session.exec(
            select(SubscriptionTier)
            .where(SubscriptionTier.creator_id == creator_id)
            .where(SubscriptionTier.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(desc(SubscriptionTier.created_at))
        ).all()

    def get_active_by_creator(
        self, session: Session, *, creator_id: UUID
    ) -> List[SubscriptionTier]:
        """Get active subscription tiers by creator."""
        return session.exec(
            select(SubscriptionTier)
            .where(SubscriptionTier.creator_id == creator_id)
            .where(SubscriptionTier.is_active == True)
            .order_by(SubscriptionTier.price_monthly)
        ).all()


class CRUDUserSubscription(
    CRUDBase[UserSubscription, UserSubscription, UserSubscription]
):
    """CRUD operations for user subscriptions."""

    def get_by_user(
        self, session: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[UserSubscription]:
        """Get subscriptions by user."""
        return session.exec(
            select(UserSubscription)
            .where(UserSubscription.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(UserSubscription.created_at))
        ).all()

    def get_active_by_user(
        self, session: Session, *, user_id: UUID
    ) -> List[UserSubscription]:
        """Get active subscriptions by user."""
        return session.exec(
            select(UserSubscription)
            .where(UserSubscription.user_id == user_id)
            .where(UserSubscription.status == "active")
            .where(UserSubscription.current_period_end > datetime.utcnow())
        ).all()

    def get_by_tier(
        self, session: Session, *, tier_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[UserSubscription]:
        """Get subscriptions by tier."""
        return session.exec(
            select(UserSubscription)
            .where(UserSubscription.tier_id == tier_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(UserSubscription.created_at))
        ).all()

    def get_expiring_soon(
        self, session: Session, *, days: int = 7
    ) -> List[UserSubscription]:
        """Get subscriptions expiring soon."""
        expiry_date = datetime.utcnow() + timedelta(days=days)
        return session.exec(
            select(UserSubscription)
            .where(UserSubscription.status == "active")
            .where(UserSubscription.current_period_end <= expiry_date)
            .where(UserSubscription.cancel_at_period_end == False)
        ).all()


class CRUDPayment(CRUDBase[Payment, Payment, Payment]):
    """CRUD operations for payments."""

    def get_by_user(
        self, session: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Payment]:
        """Get payments by user."""
        return session.exec(
            select(Payment)
            .where(Payment.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Payment.created_at))
        ).all()

    def get_by_subscription(
        self, session: Session, *, subscription_id: UUID
    ) -> List[Payment]:
        """Get payments by subscription."""
        return session.exec(
            select(Payment)
            .where(Payment.subscription_id == subscription_id)
            .order_by(desc(Payment.created_at))
        ).all()

    def get_successful_payments(
        self,
        session: Session,
        *,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Payment]:
        """Get successful payments with optional filters."""
        query = select(Payment).where(Payment.status == "completed")

        if user_id:
            query = query.where(Payment.user_id == user_id)
        if start_date:
            query = query.where(Payment.created_at >= start_date)
        if end_date:
            query = query.where(Payment.created_at <= end_date)

        return session.exec(query.order_by(desc(Payment.created_at))).all()


class CRUDAdCampaign(CRUDBase[AdCampaign, AdCampaign, AdCampaign]):
    """CRUD operations for ad campaigns."""

    def get_by_advertiser(
        self, session: Session, *, advertiser_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AdCampaign]:
        """Get campaigns by advertiser."""
        return session.exec(
            select(AdCampaign)
            .where(AdCampaign.advertiser_id == advertiser_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(AdCampaign.created_at))
        ).all()

    def get_active_campaigns(self, session: Session) -> List[AdCampaign]:
        """Get all active campaigns."""
        now = datetime.utcnow()
        return session.exec(
            select(AdCampaign)
            .where(AdCampaign.status == "active")
            .where(AdCampaign.start_date <= now)
            .where((AdCampaign.end_date.is_(None)) | (AdCampaign.end_date >= now))
            .where(AdCampaign.budget > AdCampaign.spent)
        ).all()

    def get_campaign_stats(
        self, session: Session, *, campaign_id: UUID
    ) -> Dict[str, Any]:
        """Get campaign statistics."""
        result = session.exec(
            select(
                func.count(AdImpression.id).label("impressions"),
                func.sum(AdImpression.cost).label("total_cost"),
                func.count(func.distinct(AdImpression.user_id)).label("unique_users"),
            )
            .select_from(AdImpression)
            .where(AdImpression.campaign_id == campaign_id)
        ).first()

        return {
            "impressions": result.impressions or 0,
            "total_cost": result.total_cost or 0,
            "unique_users": result.unique_users or 0,
        }


class CRUDAdImpression(CRUDBase[AdImpression, AdImpression, AdImpression]):
    """CRUD operations for ad impressions."""

    def get_by_campaign(
        self, session: Session, *, campaign_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AdImpression]:
        """Get impressions by campaign."""
        return session.exec(
            select(AdImpression)
            .where(AdImpression.campaign_id == campaign_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(AdImpression.created_at))
        ).all()

    def get_campaign_cost(
        self,
        session: Session,
        *,
        campaign_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> float:
        """Get total cost for a campaign in a date range."""
        query = select(func.sum(AdImpression.cost)).where(
            AdImpression.campaign_id == campaign_id
        )

        if start_date:
            query = query.where(AdImpression.created_at >= start_date)
        if end_date:
            query = query.where(AdImpression.created_at <= end_date)

        result = session.exec(query).first()
        return result or 0


class CRUDCreatorEarning(CRUDBase[CreatorEarning, CreatorEarning, CreatorEarning]):
    """CRUD operations for creator earnings."""

    def get_by_creator(
        self, session: Session, *, creator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[CreatorEarning]:
        """Get earnings by creator."""
        return session.exec(
            select(CreatorEarning)
            .where(CreatorEarning.creator_id == creator_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(CreatorEarning.created_at))
        ).all()

    def get_unpaid_earnings(
        self, session: Session, *, creator_id: UUID
    ) -> List[CreatorEarning]:
        """Get unpaid earnings for a creator."""
        return session.exec(
            select(CreatorEarning)
            .where(CreatorEarning.creator_id == creator_id)
            .where(CreatorEarning.status == "pending")
            .where(CreatorEarning.payout_id.is_(None))
        ).all()

    def get_earnings_summary(
        self,
        session: Session,
        *,
        creator_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get earnings summary for a creator."""
        query = select(
            func.sum(CreatorEarning.amount).label("total_earnings"),
            func.count(CreatorEarning.id).label("transaction_count"),
        ).where(CreatorEarning.creator_id == creator_id)

        if start_date:
            query = query.where(CreatorEarning.created_at >= start_date)
        if end_date:
            query = query.where(CreatorEarning.created_at <= end_date)

        result = session.exec(query).first()

        return {
            "total_earnings": result.total_earnings or 0,
            "transaction_count": result.transaction_count or 0,
        }


class CRUDCreatorPayout(CRUDBase[CreatorPayout, CreatorPayout, CreatorPayout]):
    """CRUD operations for creator payouts."""

    def get_by_creator(
        self, session: Session, *, creator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[CreatorPayout]:
        """Get payouts by creator."""
        return session.exec(
            select(CreatorPayout)
            .where(CreatorPayout.creator_id == creator_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(CreatorPayout.created_at))
        ).all()

    def get_pending_payouts(self, session: Session) -> List[CreatorPayout]:
        """Get all pending payouts."""
        return session.exec(
            select(CreatorPayout)
            .where(CreatorPayout.status == "pending")
            .order_by(CreatorPayout.created_at)
        ).all()


class CRUDSponsoredContent(
    CRUDBase[SponsoredContent, SponsoredContent, SponsoredContent]
):
    """CRUD operations for sponsored content."""

    def get_by_creator(
        self, session: Session, *, creator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[SponsoredContent]:
        """Get sponsored content by creator."""
        return session.exec(
            select(SponsoredContent)
            .where(SponsoredContent.creator_id == creator_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(SponsoredContent.created_at))
        ).all()

    def get_by_brand(
        self, session: Session, *, brand_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[SponsoredContent]:
        """Get sponsored content by brand."""
        return session.exec(
            select(SponsoredContent)
            .where(SponsoredContent.brand_id == brand_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(SponsoredContent.created_at))
        ).all()


class CRUDPremiumFeature(CRUDBase[PremiumFeature, PremiumFeature, PremiumFeature]):
    """CRUD operations for premium features."""

    def get_active_features(self, session: Session) -> List[PremiumFeature]:
        """Get all active premium features."""
        return session.exec(
            select(PremiumFeature)
            .where(PremiumFeature.is_active == True)
            .order_by(PremiumFeature.price)
        ).all()

    def get_by_type(
        self, session: Session, *, feature_type: str
    ) -> List[PremiumFeature]:
        """Get features by type."""
        return session.exec(
            select(PremiumFeature)
            .where(PremiumFeature.feature_type == feature_type)
            .where(PremiumFeature.is_active == True)
            .order_by(PremiumFeature.price)
        ).all()


class CRUDPremiumFeaturePurchase(
    CRUDBase[PremiumFeaturePurchase, PremiumFeaturePurchase, PremiumFeaturePurchase]
):
    """CRUD operations for premium feature purchases."""

    def get_by_user(
        self, session: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PremiumFeaturePurchase]:
        """Get purchases by user."""
        return session.exec(
            select(PremiumFeaturePurchase)
            .where(PremiumFeaturePurchase.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(PremiumFeaturePurchase.created_at))
        ).all()

    def get_active_by_user(
        self, session: Session, *, user_id: UUID
    ) -> List[PremiumFeaturePurchase]:
        """Get active purchases by user."""
        now = datetime.utcnow()
        return session.exec(
            select(PremiumFeaturePurchase)
            .where(PremiumFeaturePurchase.user_id == user_id)
            .where(PremiumFeaturePurchase.status == "active")
            .where(
                (PremiumFeaturePurchase.expires_at.is_(None))
                | (PremiumFeaturePurchase.expires_at > now)
            )
            .where(
                (PremiumFeaturePurchase.usage_limit.is_(None))
                | (
                    PremiumFeaturePurchase.usage_count
                    < PremiumFeaturePurchase.usage_limit
                )
            )
        ).all()

    def get_by_feature(
        self, session: Session, *, feature_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PremiumFeaturePurchase]:
        """Get purchases by feature."""
        return session.exec(
            select(PremiumFeaturePurchase)
            .where(PremiumFeaturePurchase.feature_id == feature_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(PremiumFeaturePurchase.created_at))
        ).all()


# Create singleton instances
crud_subscription_tier = CRUDSubscriptionTier(SubscriptionTier)
crud_user_subscription = CRUDUserSubscription(UserSubscription)
crud_payment = CRUDPayment(Payment)
crud_ad_campaign = CRUDAdCampaign(AdCampaign)
crud_ad_impression = CRUDAdImpression(AdImpression)
crud_creator_earning = CRUDCreatorEarning(CreatorEarning)
crud_creator_payout = CRUDCreatorPayout(CreatorPayout)
crud_sponsored_content = CRUDSponsoredContent(SponsoredContent)
crud_premium_feature = CRUDPremiumFeature(PremiumFeature)
crud_premium_feature_purchase = CRUDPremiumFeaturePurchase(PremiumFeaturePurchase)
