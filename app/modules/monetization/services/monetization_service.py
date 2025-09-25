from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session

from app.modules.monetization.crud import (
    crud_ad_campaign,
    crud_ad_impression,
    crud_creator_earning,
    crud_creator_payout,
    crud_payment,
    crud_premium_feature,
    crud_premium_feature_purchase,
    crud_sponsored_content,
    crud_subscription_tier,
    crud_user_subscription,
)
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
from app.modules.monetization.schema.monetization import (
    AdCampaignCreate,
    AdImpressionCreate,
    CreatorDashboard,
    CreatorEarningCreate,
    CreatorPayoutCreate,
    PaymentCreate,
    PremiumFeatureCreate,
    PremiumFeaturePurchaseCreate,
    RevenueAnalytics,
    SponsoredContentCreate,
    SubscriptionCheckout,
    SubscriptionTierCreate,
    UserSubscriptionCreate,
)


class SubscriptionService:
    """Service for subscription management."""

    @staticmethod
    def create_subscription_tier(
        session: Session, creator_id: UUID, tier_data: SubscriptionTierCreate
    ) -> SubscriptionTier:
        """Create a new subscription tier."""
        tier = SubscriptionTier(creator_id=creator_id, **tier_data.model_dump())
        return crud_subscription_tier.create(session, obj_in=tier)

    @staticmethod
    def get_creator_tiers(session: Session, creator_id: UUID) -> List[SubscriptionTier]:
        """Get all active tiers for a creator."""
        return crud_subscription_tier.get_active_by_creator(
            session, creator_id=creator_id
        )

    @staticmethod
    def subscribe_user(
        session: Session, user_id: UUID, checkout_data: SubscriptionCheckout
    ) -> UserSubscription:
        """Subscribe a user to a tier."""
        # Get the tier
        tier = crud_subscription_tier.get(session, id=checkout_data.tier_id)
        if not tier or not tier.is_active:
            raise ValueError("Subscription tier not found or inactive")

        # Check if user is already subscribed to this tier
        existing_subscription = session.exec(
            session.query(UserSubscription)
            .where(UserSubscription.user_id == user_id)
            .where(UserSubscription.tier_id == checkout_data.tier_id)
            .where(UserSubscription.status == "active")
        ).first()

        if existing_subscription:
            raise ValueError("User is already subscribed to this tier")

        # Calculate subscription period
        now = datetime.utcnow()
        if checkout_data.billing_cycle == "yearly" and tier.price_yearly:
            price = tier.price_yearly
            period_end = now + timedelta(days=365)
        else:
            price = tier.price_monthly
            period_end = now + timedelta(days=30)

        # Create subscription
        subscription = UserSubscription(
            user_id=user_id,
            tier_id=checkout_data.tier_id,
            current_period_start=now,
            current_period_end=period_end,
        )
        subscription = crud_user_subscription.create(session, obj_in=subscription)

        # Create payment record
        payment = Payment(
            user_id=user_id,
            subscription_id=subscription.id,
            amount=price,
            currency="USD",
            payment_method=checkout_data.payment_method,
            payment_id=f"sub_{subscription.id}_{now.timestamp()}",  # Mock payment ID
            description=f"Subscription to {tier.name}",
        )
        crud_payment.create(session, obj_in=payment)

        # Create earning for creator
        earning = CreatorEarning(
            creator_id=tier.creator_id,
            source_type="subscription",
            source_id=subscription.id,
            amount=price * Decimal("0.9"),  # 90% goes to creator
            currency="USD",
        )
        crud_creator_earning.create(session, obj_in=earning)

        return subscription

    @staticmethod
    def cancel_subscription(
        session: Session, subscription_id: UUID, user_id: UUID
    ) -> UserSubscription:
        """Cancel a user subscription."""
        subscription = crud_user_subscription.get(session, id=subscription_id)
        if not subscription or subscription.user_id != user_id:
            raise ValueError("Subscription not found")

        subscription.cancel_at_period_end = True
        subscription.cancelled_at = datetime.utcnow()
        return crud_user_subscription.update(
            session,
            db_obj=subscription,
            obj_in={"cancel_at_period_end": True, "cancelled_at": datetime.utcnow()},
        )


class PaymentService:
    """Service for payment processing."""

    @staticmethod
    def process_payment(
        session: Session,
        payment_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Payment:
        """Process a payment update."""
        payment = session.exec(
            session.query(Payment).where(Payment.payment_id == payment_id)
        ).first()

        if not payment:
            raise ValueError("Payment not found")

        payment.status = status
        if metadata:
            payment.metadata.update(metadata)

        return crud_payment.update(
            session,
            db_obj=payment,
            obj_in={"status": status, "metadata": payment.metadata},
        )

    @staticmethod
    def get_user_payment_history(
        session: Session, user_id: UUID, limit: int = 50
    ) -> List[Payment]:
        """Get payment history for a user."""
        return crud_payment.get_by_user(session, user_id=user_id, limit=limit)


class AdService:
    """Service for advertising campaigns."""

    @staticmethod
    def create_campaign(
        session: Session, advertiser_id: UUID, campaign_data: AdCampaignCreate
    ) -> AdCampaign:
        """Create a new ad campaign."""
        campaign = AdCampaign(advertiser_id=advertiser_id, **campaign_data.model_dump())
        return crud_ad_campaign.create(session, obj_in=campaign)

    @staticmethod
    def record_impression(
        session: Session, impression_data: AdImpressionCreate
    ) -> AdImpression:
        """Record an ad impression."""
        # Get campaign and check if active
        campaign = crud_ad_campaign.get(session, id=impression_data.campaign_id)
        if not campaign or campaign.status != "active":
            raise ValueError("Campaign not found or inactive")

        # Calculate cost (simplified: $0.001 per impression)
        cost = Decimal("0.001")

        # Check budget
        if campaign.spent + cost > campaign.budget:
            raise ValueError("Campaign budget exceeded")

        # Create impression
        impression = AdImpression(
            campaign_id=impression_data.campaign_id,
            content_id=impression_data.content_id,
            content_type=impression_data.content_type,
            impression_type=impression_data.impression_type,
            cost=cost,
        )
        impression = crud_ad_impression.create(session, obj_in=impression)

        # Update campaign spent amount
        campaign.spent += cost
        crud_ad_campaign.update(
            session, db_obj=campaign, obj_in={"spent": campaign.spent}
        )

        return impression

    @staticmethod
    def get_campaign_analytics(session: Session, campaign_id: UUID) -> Dict[str, Any]:
        """Get analytics for a campaign."""
        return crud_ad_campaign.get_campaign_stats(session, campaign_id=campaign_id)


class CreatorService:
    """Service for creator monetization features."""

    @staticmethod
    def get_creator_dashboard(session: Session, creator_id: UUID) -> CreatorDashboard:
        """Get dashboard data for a creator."""
        # Get subscription count
        subscriptions = crud_user_subscription.get_active_by_user(
            session, user_id=creator_id
        )
        total_subscribers = len(subscriptions)

        # Get earnings summary for current month
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        earnings_summary = crud_creator_earning.get_earnings_summary(
            session, creator_id=creator_id, start_date=start_of_month
        )

        # Get pending payouts
        unpaid_earnings = crud_creator_earning.get_unpaid_earnings(
            session, creator_id=creator_id
        )
        pending_payouts = sum(earning.amount for earning in unpaid_earnings)

        # Get active campaigns and sponsored content
        campaigns = crud_ad_campaign.get_by_advertiser(
            session, advertiser_id=creator_id
        )
        active_campaigns = len([c for c in campaigns if c.status == "active"])

        sponsored = crud_sponsored_content.get_by_creator(
            session, creator_id=creator_id
        )
        sponsored_posts = len([s for s in sponsored if s.status == "active"])

        return CreatorDashboard(
            total_subscribers=total_subscribers,
            monthly_revenue=earnings_summary["total_earnings"],
            total_earnings=earnings_summary["total_earnings"],  # Simplified
            pending_payouts=pending_payouts,
            active_campaigns=active_campaigns,
            sponsored_posts=sponsored_posts,
        )

    @staticmethod
    def create_payout(
        session: Session, creator_id: UUID, period_start: datetime, period_end: datetime
    ) -> CreatorPayout:
        """Create a payout for a creator."""
        # Get unpaid earnings for the period
        earnings = session.exec(
            session.query(CreatorEarning)
            .where(CreatorEarning.creator_id == creator_id)
            .where(CreatorEarning.status == "pending")
            .where(CreatorEarning.created_at >= period_start)
            .where(CreatorEarning.created_at <= period_end)
        ).all()

        if not earnings:
            raise ValueError("No earnings available for payout")

        total_amount = sum(earning.amount for earning in earnings)

        # Create payout
        payout = CreatorPayout(
            creator_id=creator_id,
            amount=total_amount,
            currency="USD",
            payout_method="bank_transfer",  # Default
            period_start=period_start,
            period_end=period_end,
        )
        payout = crud_creator_payout.create(session, obj_in=payout)

        # Update earnings with payout ID
        for earning in earnings:
            crud_creator_earning.update(
                session, db_obj=earning, obj_in={"payout_id": payout.id}
            )

        return payout

    @staticmethod
    def get_revenue_analytics(
        session: Session,
        creator_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> RevenueAnalytics:
        """Get revenue analytics for a creator."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Get earnings by type
        earnings = session.exec(
            session.query(CreatorEarning)
            .where(CreatorEarning.creator_id == creator_id)
            .where(CreatorEarning.created_at >= start_date)
            .where(CreatorEarning.created_at <= end_date)
        ).all()

        subscription_revenue = sum(
            e.amount for e in earnings if e.source_type == "subscription"
        )
        ad_revenue = sum(e.amount for e in earnings if e.source_type == "ad_revenue")
        sponsored_revenue = sum(
            e.amount for e in earnings if e.source_type == "sponsored"
        )

        total_earnings = subscription_revenue + ad_revenue + sponsored_revenue

        return RevenueAnalytics(
            total_earnings=total_earnings,
            monthly_earnings=total_earnings,  # Simplified
            subscription_revenue=subscription_revenue,
            ad_revenue=ad_revenue,
            sponsored_revenue=sponsored_revenue,
            period_start=start_date,
            period_end=end_date,
        )


class SponsoredContentService:
    """Service for sponsored content management."""

    @staticmethod
    def create_sponsored_content(
        session: Session, creator_id: UUID, sponsored_data: SponsoredContentCreate
    ) -> SponsoredContent:
        """Create sponsored content."""
        sponsored = SponsoredContent(
            creator_id=creator_id, **sponsored_data.model_dump()
        )
        return crud_sponsored_content.create(session, obj_in=sponsored)

    @staticmethod
    def approve_sponsored_content(
        session: Session, content_id: UUID, creator_id: UUID
    ) -> SponsoredContent:
        """Approve sponsored content."""
        content = crud_sponsored_content.get(session, id=content_id)
        if not content or content.creator_id != creator_id:
            raise ValueError("Sponsored content not found")

        return crud_sponsored_content.update(
            session, db_obj=content, obj_in={"status": "active"}
        )


class PremiumFeatureService:
    """Service for premium features."""

    @staticmethod
    def purchase_feature(
        session: Session, user_id: UUID, feature_id: UUID, payment_method: str
    ) -> PremiumFeaturePurchase:
        """Purchase a premium feature."""
        # Get the feature
        feature = crud_premium_feature.get(session, id=feature_id)
        if not feature or not feature.is_active:
            raise ValueError("Premium feature not found or inactive")

        # Check if user already has this feature
        existing_purchase = session.exec(
            session.query(PremiumFeaturePurchase)
            .where(PremiumFeaturePurchase.user_id == user_id)
            .where(PremiumFeaturePurchase.feature_id == feature_id)
            .where(PremiumFeaturePurchase.status == "active")
        ).first()

        if existing_purchase:
            raise ValueError("User already has this premium feature")

        # Create purchase
        purchase = PremiumFeaturePurchase(
            user_id=user_id,
            feature_id=feature_id,
            expires_at=datetime.utcnow() + timedelta(days=30),  # 30-day expiration
        )
        purchase = crud_premium_feature_purchase.create(session, obj_in=purchase)

        # Create payment record
        payment = Payment(
            user_id=user_id,
            amount=feature.price,
            currency=feature.currency,
            payment_method=payment_method,
            payment_id=f"premium_{purchase.id}_{datetime.utcnow().timestamp()}",
            description=f"Premium feature: {feature.name}",
        )
        crud_payment.create(session, obj_in=payment)

        return purchase

    @staticmethod
    def check_feature_access(
        session: Session, user_id: UUID, feature_type: str
    ) -> bool:
        """Check if user has access to a premium feature type."""
        active_purchases = crud_premium_feature_purchase.get_active_by_user(
            session, user_id=user_id
        )

        # Check if any purchase gives access to this feature type
        for purchase in active_purchases:
            feature = crud_premium_feature.get(session, id=purchase.feature_id)
            if feature and feature.feature_type == feature_type:
                return True

        return False
