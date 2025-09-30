from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.modules.monetization.crud import (
    crud_ad_campaign,
    crud_creator_earning,
    crud_payment,
    crud_premium_feature,
    crud_premium_feature_purchase,
    crud_sponsored_content,
    crud_subscription_tier,
    crud_user_subscription,
)
from app.modules.monetization.model.monetization import (
    AdCampaign,
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
    AdCampaignPublic,
    AdCampaignUpdate,
    AdImpressionCreate,
    CreatorDashboard,
    CreatorEarningPublic,
    CreatorPayoutPublic,
    PaymentPublic,
    PremiumFeatureCreate,
    PremiumFeaturePublic,
    PremiumFeaturePurchasePublic,
    PremiumFeatureUpdate,
    RevenueAnalytics,
    SponsoredContentCreate,
    SponsoredContentPublic,
    SubscriptionCheckout,
    SubscriptionTierCreate,
    SubscriptionTierPublic,
    SubscriptionTierUpdate,
    UserSubscriptionPublic,
)
from app.modules.monetization.services import (
    AdService,
    CreatorService,
    PremiumFeatureService,
    SponsoredContentService,
    SubscriptionService,
)
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


# Subscription Tiers Routes
@router.post("/tiers", response_model=SubscriptionTierPublic)
def create_subscription_tier(
    *, session: SessionDep, current_user: CurrentUser, tier_in: SubscriptionTierCreate
) -> SubscriptionTier:
    """
    Create a new subscription tier.
    """
    return SubscriptionService.create_subscription_tier(
        session=session, creator_id=current_user.id, tier_data=tier_in
    )


@router.get("/tiers", response_model=List[SubscriptionTierPublic])
def read_subscription_tiers(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    creator_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[SubscriptionTier]:
    """
    Retrieve subscription tiers.
    """
    if creator_id:
        return crud_subscription_tier.get_by_creator(
            session=session, creator_id=creator_id, skip=skip, limit=limit
        )
    else:
        # Get current user's tiers
        return crud_subscription_tier.get_by_creator(
            session=session, creator_id=current_user.id, skip=skip, limit=limit
        )


@router.get("/tiers/{tier_id}", response_model=SubscriptionTierPublic)
def read_subscription_tier(
    *, session: SessionDep, current_user: CurrentUser, tier_id: UUID
) -> SubscriptionTier:
    """
    Get a specific subscription tier.
    """
    tier = crud_subscription_tier.get(session=session, id=tier_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Subscription tier not found")
    return tier


@router.put("/tiers/{tier_id}", response_model=SubscriptionTierPublic)
def update_subscription_tier(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    tier_id: UUID,
    tier_in: SubscriptionTierUpdate,
) -> SubscriptionTier:
    """
    Update a subscription tier.
    """
    tier = crud_subscription_tier.get(session=session, id=tier_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Subscription tier not found")

    if tier.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    tier = crud_subscription_tier.update(
        session=session, db_obj=tier, obj_in=tier_in.model_dump(exclude_unset=True)
    )
    return tier


@router.delete("/tiers/{tier_id}")
def delete_subscription_tier(
    *, session: SessionDep, current_user: CurrentUser, tier_id: UUID
) -> dict:
    """
    Delete a subscription tier.
    """
    tier = crud_subscription_tier.get(session=session, id=tier_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Subscription tier not found")

    if tier.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud_subscription_tier.remove(session=session, id=tier_id)
    return {"message": "Subscription tier deleted successfully"}


# User Subscriptions Routes
@router.post("/subscribe", response_model=UserSubscriptionPublic)
def subscribe_to_tier(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    checkout_data: SubscriptionCheckout,
) -> UserSubscription:
    """
    Subscribe to a creator's tier.
    """
    try:
        return SubscriptionService.subscribe_user(
            session=session, user_id=current_user.id, checkout_data=checkout_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscriptions", response_model=List[UserSubscriptionPublic])
def read_user_subscriptions(
    *, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[UserSubscription]:
    """
    Get user's subscriptions.
    """
    return crud_user_subscription.get_by_user(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )


@router.post("/subscriptions/{subscription_id}/cancel")
def cancel_subscription(
    *, session: SessionDep, current_user: CurrentUser, subscription_id: UUID
) -> dict:
    """
    Cancel a subscription.
    """
    try:
        SubscriptionService.cancel_subscription(
            session=session, subscription_id=subscription_id, user_id=current_user.id
        )
        return {"message": "Subscription cancelled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Payments Routes
@router.get("/payments", response_model=List[PaymentPublic])
def read_user_payments(
    *, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[Payment]:
    """
    Get user's payment history.
    """
    return crud_payment.get_by_user(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )


# Ad Campaigns Routes
@router.post("/campaigns", response_model=AdCampaignPublic)
def create_ad_campaign(
    *, session: SessionDep, current_user: CurrentUser, campaign_in: AdCampaignCreate
) -> AdCampaign:
    """
    Create a new ad campaign.
    """
    return AdService.create_campaign(
        session=session, advertiser_id=current_user.id, campaign_data=campaign_in
    )


@router.get("/campaigns", response_model=List[AdCampaignPublic])
def read_ad_campaigns(
    *, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[AdCampaign]:
    """
    Get user's ad campaigns.
    """
    return crud_ad_campaign.get_by_advertiser(
        session=session, advertiser_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/campaigns/{campaign_id}", response_model=AdCampaignPublic)
def read_ad_campaign(
    *, session: SessionDep, current_user: CurrentUser, campaign_id: UUID
) -> AdCampaign:
    """
    Get a specific ad campaign.
    """
    campaign = crud_ad_campaign.get(session=session, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Ad campaign not found")

    if campaign.advertiser_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return campaign


@router.put("/campaigns/{campaign_id}", response_model=AdCampaignPublic)
def update_ad_campaign(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    campaign_id: UUID,
    campaign_in: AdCampaignUpdate,
) -> AdCampaign:
    """
    Update an ad campaign.
    """
    campaign = crud_ad_campaign.get(session=session, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Ad campaign not found")

    if campaign.advertiser_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    campaign = crud_ad_campaign.update(
        session=session,
        db_obj=campaign,
        obj_in=campaign_in.model_dump(exclude_unset=True),
    )
    return campaign


@router.get("/campaigns/{campaign_id}/analytics")
def get_campaign_analytics(
    *, session: SessionDep, current_user: CurrentUser, campaign_id: UUID
) -> dict:
    """
    Get analytics for an ad campaign.
    """
    campaign = crud_ad_campaign.get(session=session, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Ad campaign not found")

    if campaign.advertiser_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return AdService.get_campaign_analytics(session=session, campaign_id=campaign_id)


# Creator Dashboard Routes
@router.get("/creator/dashboard", response_model=CreatorDashboard)
def get_creator_dashboard(
    *, session: SessionDep, current_user: CurrentUser
) -> CreatorDashboard:
    """
    Get creator dashboard data.
    """
    return CreatorService.get_creator_dashboard(
        session=session, creator_id=current_user.id
    )


@router.get("/creator/analytics", response_model=RevenueAnalytics)
def get_creator_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> RevenueAnalytics:
    """
    Get creator revenue analytics.
    """
    from datetime import datetime

    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    return CreatorService.get_revenue_analytics(
        session=session, creator_id=current_user.id, start_date=start, end_date=end
    )


@router.get("/creator/earnings", response_model=List[CreatorEarningPublic])
def read_creator_earnings(
    *, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[CreatorEarning]:
    """
    Get creator earnings.
    """
    return crud_creator_earning.get_by_creator(
        session=session, creator_id=current_user.id, skip=skip, limit=limit
    )


@router.post("/creator/payouts", response_model=CreatorPayoutPublic)
def create_creator_payout(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    period_start: str,
    period_end: str,
) -> CreatorPayout:
    """
    Create a payout for creator earnings.
    """
    from datetime import datetime

    try:
        start = datetime.fromisoformat(period_start)
        end = datetime.fromisoformat(period_end)

        return CreatorService.create_payout(
            session=session,
            creator_id=current_user.id,
            period_start=start,
            period_end=end,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")


# Sponsored Content Routes
@router.post("/sponsored", response_model=SponsoredContentPublic)
def create_sponsored_content(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    sponsored_in: SponsoredContentCreate,
) -> SponsoredContent:
    """
    Create sponsored content.
    """
    return SponsoredContentService.create_sponsored_content(
        session=session, creator_id=current_user.id, sponsored_data=sponsored_in
    )


@router.get("/sponsored", response_model=List[SponsoredContentPublic])
def read_sponsored_content(
    *, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[SponsoredContent]:
    """
    Get user's sponsored content.
    """
    return crud_sponsored_content.get_by_creator(
        session=session, creator_id=current_user.id, skip=skip, limit=limit
    )


@router.put("/sponsored/{content_id}/approve")
def approve_sponsored_content(
    *, session: SessionDep, current_user: CurrentUser, content_id: UUID
) -> dict:
    """
    Approve sponsored content.
    """
    try:
        SponsoredContentService.approve_sponsored_content(
            session=session, content_id=content_id, creator_id=current_user.id
        )
        return {"message": "Sponsored content approved successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Premium Features Routes
@router.get("/premium/features", response_model=List[PremiumFeaturePublic])
def read_premium_features(
    *, session: SessionDep, current_user: CurrentUser
) -> List[PremiumFeature]:
    """
    Get available premium features.
    """
    return crud_premium_feature.get_active_features(session=session)


@router.post("/premium/purchase", response_model=PremiumFeaturePurchasePublic)
def purchase_premium_feature(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    feature_id: UUID,
    payment_method: str = Query(..., description="Payment method"),
) -> PremiumFeaturePurchase:
    """
    Purchase a premium feature.
    """
    try:
        return PremiumFeatureService.purchase_feature(
            session=session,
            user_id=current_user.id,
            feature_id=feature_id,
            payment_method=payment_method,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/premium/purchases", response_model=List[PremiumFeaturePurchasePublic])
def read_premium_purchases(
    *, session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[PremiumFeaturePurchase]:
    """
    Get user's premium feature purchases.
    """
    return crud_premium_feature_purchase.get_by_user(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/premium/check-access/{feature_type}")
def check_premium_access(
    *, session: SessionDep, current_user: CurrentUser, feature_type: str
) -> dict:
    """
    Check if user has access to a premium feature type.
    """
    has_access = PremiumFeatureService.check_feature_access(
        session=session, user_id=current_user.id, feature_type=feature_type
    )
    return {"has_access": has_access}


# Admin Routes
@router.post("/impressions", response_model=dict)
def record_ad_impression(
    *, session: SessionDep, impression_in: AdImpressionCreate
) -> dict:
    """
    Record an ad impression (internal use).
    """
    try:
        impression = AdService.record_impression(
            session=session, impression_data=impression_in
        )
        return {"message": "Impression recorded", "impression_id": impression.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/premium/features", response_model=PremiumFeaturePublic)
def create_premium_feature(
    *, session: SessionDep, current_user: CurrentUser, feature_in: PremiumFeatureCreate
) -> PremiumFeature:
    """
    Create a premium feature (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return crud_premium_feature.create(session=session, obj_in=feature_in)


@router.put("/premium/features/{feature_id}", response_model=PremiumFeaturePublic)
def update_premium_feature(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    feature_id: UUID,
    feature_in: PremiumFeatureUpdate,
) -> PremiumFeature:
    """
    Update a premium feature (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    feature = crud_premium_feature.get(session=session, id=feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Premium feature not found")

    return crud_premium_feature.update(
        session=session,
        db_obj=feature,
        obj_in=feature_in.model_dump(exclude_unset=True),
    )
