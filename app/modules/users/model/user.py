import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

# Import models that have relationships with User to avoid forward reference issues
from app.modules.auth.model.auth import UserCredentials  # noqa: E402
from app.modules.auth.model.token import Token  # noqa: E402
from app.modules.content_moderation.model.moderation import (
    BanAppeal,
    ContentFlag,
    ContentReport,
    ModerationAction,
    ModerationAppeal,
    ModerationLog,
    UserBan,
    UserStrike,
)
from app.modules.news.model.factcheck import FactCheck  # noqa: E402
from app.modules.posts.model.bookmark import Bookmark  # noqa: E402
from app.modules.posts.model.like import Like  # noqa: E402
from app.modules.social.model.comment import Comment  # noqa: E402
from app.modules.users.schema.user import UserBase
from app.shared.enums.account_type import AccountType
from app.shared.enums.gender import Gender

if TYPE_CHECKING:
    from app.modules.ai_features.model.ai_features import (
        ChurnPrediction,
        ContentRecommendation,
        PersonalizedFeed,
        UserBehavior,
    )
    from app.modules.content_moderation.model.moderation import BanAppeal  # UserBan,
    from app.modules.content_moderation.model.moderation import (
        ContentFlag,
        ContentReport,
        ModerationAction,
        ModerationAppeal,
        ModerationLog,
        UserStrike,
    )
    from app.modules.live_streams.model.stream import Stream
    from app.modules.monetization.model.monetization import (
        AdCampaign,
        AdImpression,
        CreatorEarning,
        CreatorPayout,
        Payment,
        PremiumFeaturePurchase,
        SponsoredContent,
        SubscriptionTier,
        UserSubscription,
    )
    from app.modules.news.model.news import News
    from app.modules.notifications.model.device import Device
    from app.modules.notifications.model.notification import Notification
    from app.modules.notifications.model.preference import NotificationPreference
    from app.modules.posts.model.post import Post
    from app.modules.reels.model.reel import Reel
    from app.modules.search.model.history import SearchHistory
    from app.modules.search.model.search import SearchQuery
    from app.modules.stories.model.highlight import StoryHighlight
    from app.modules.stories.model.story import Story
    from app.modules.users.model.profile import Profile, ProfileView
    from app.modules.users.model.verification import (
        VerificationBadge,
        VerificationRequest,
    )


class User(UserBase, table=True):
    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Authentication Fields
    username: str = Field(unique=True, index=True, max_length=50, default="")
    email: str = Field(unique=True, index=True, max_length=100, default="")
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    # Profile Information
    full_name: Optional[str] = Field(default=None, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    profile_image_url: Optional[str] = Field(default=None, max_length=255)
    website_url: Optional[str] = Field(default=None, max_length=255)
    location: Optional[str] = Field(default=None, max_length=100)
    birth_date: Optional[datetime] = Field(default=None)
    gender: Optional[Gender] = Field(default=None)

    # Account Settings
    account_type: AccountType = Field(default=AccountType.personal)
    is_private: bool = Field(default=False)
    is_professional_account: bool = Field(default=False)
    category: Optional[str] = Field(
        default=None, max_length=50
    )  # For business accounts

    # User Type Flags
    is_journalist: bool = Field(default=False)
    is_organization: bool = Field(default=False)

    # Social Media Counters
    follower_count: int = Field(default=0)
    following_count: int = Field(default=0)
    post_count: int = Field(default=0)

    # Metadata
    last_active: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    posts: List["Post"] = Relationship(back_populates="owner", cascade_delete=True)
    news: List["News"] = Relationship(back_populates="author", cascade_delete=True)
    comments: List["Comment"] = Relationship(
        back_populates="author", cascade_delete=True
    )
    likes: List["Like"] = Relationship(back_populates="user", cascade_delete=True)
    bookmarks: List["Bookmark"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    stories: List["Story"] = Relationship(back_populates="user", cascade_delete=True)
    reels: List["Reel"] = Relationship(back_populates="user", cascade_delete=True)

    # Social Relationships (through association tables)
    followers: List["Follow"] = Relationship(
        back_populates="following",
        sa_relationship_kwargs={"foreign_keys": "Follow.following_id"},
    )
    following: List["Follow"] = Relationship(
        back_populates="follower",
        sa_relationship_kwargs={"foreign_keys": "Follow.follower_id"},
    )

    # Notification relationships
    received_notifications: List["Notification"] = Relationship(
        back_populates="recipient",
        sa_relationship_kwargs={"foreign_keys": "Notification.recipient_id"},
    )
    sent_notifications: List["Notification"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={"foreign_keys": "Notification.sender_id"},
    )
    devices: List["Device"] = Relationship(back_populates="user", cascade_delete=True)
    tokens: List["Token"] = Relationship(back_populates="user", cascade_delete=True)
    notification_preferences: Optional["NotificationPreference"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # Search relationships
    search_queries: List["SearchQuery"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    search_history: List["SearchHistory"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # AI Features relationships
    content_recommendations: List["ContentRecommendation"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    behavior_logs: List["UserBehavior"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # Auth relationships
    credentials: Optional["UserCredentials"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # Moderation relationships
    bans: List["UserBan"] = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[UserBan.user_id]"},
    )
    banned_users: List["UserBan"] = Relationship(
        back_populates="banner",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[UserBan.banned_by]"},
    )

    # Additional AI Features relationships
    personalized_feed: Optional["PersonalizedFeed"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    churn_predictions: List["ChurnPrediction"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # Content Moderation relationships
    reports_made: List["ContentReport"] = Relationship(
        back_populates="reporter",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[ContentReport.reporter_id]"},
    )
    reports_reviewed: List["ContentReport"] = Relationship(
        back_populates="reviewer",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[ContentReport.reviewed_by]"},
    )
    moderation_actions: List["ModerationAction"] = Relationship(
        back_populates="moderator",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[ModerationAction.moderator_id]"},
    )
    moderation_appeals: List["ModerationAppeal"] = Relationship(
        back_populates="appellant",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[ModerationAppeal.appellant_id]"},
    )
    appeal_reviews: List["ModerationAppeal"] = Relationship(
        back_populates="reviewer",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[ModerationAppeal.reviewed_by]"},
    )
    resolved_flags: List["ContentFlag"] = Relationship(
        back_populates="resolver",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[ContentFlag.resolved_by]"},
    )
    strikes: List["UserStrike"] = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[UserStrike.user_id]"},
    )
    issued_strikes: List["UserStrike"] = Relationship(
        back_populates="issuer",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[UserStrike.issued_by]"},
    )
    ban_appeals: List["BanAppeal"] = Relationship(
        back_populates="appellant",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[BanAppeal.appellant_id]"},
    )
    ban_appeal_reviews: List["BanAppeal"] = Relationship(
        back_populates="reviewer",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[BanAppeal.reviewed_by]"},
    )
    moderation_logs: List["ModerationLog"] = Relationship(
        back_populates="moderator",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[ModerationLog.moderator_id]"},
    )

    # Fact checking relationships
    fact_checks: List["FactCheck"] = Relationship(
        back_populates="checker",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[FactCheck.user_id]"},
    )
    organization_fact_checks: List["FactCheck"] = Relationship(
        back_populates="organization",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[FactCheck.organization_id]"},
    )

    # Monetization relationships
    subscription_tiers: List["SubscriptionTier"] = Relationship(
        back_populates="creator", cascade_delete=True
    )
    subscriptions: List["UserSubscription"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    payments: List["Payment"] = Relationship(back_populates="user", cascade_delete=True)
    ad_campaigns: List["AdCampaign"] = Relationship(
        back_populates="advertiser", cascade_delete=True
    )
    ad_impressions: List["AdImpression"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    earnings: List["CreatorEarning"] = Relationship(
        back_populates="creator", cascade_delete=True
    )
    payouts: List["CreatorPayout"] = Relationship(
        back_populates="creator", cascade_delete=True
    )
    sponsored_content: List["SponsoredContent"] = Relationship(
        back_populates="creator",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[SponsoredContent.creator_id]"},
    )
    brand_sponsorships: List["SponsoredContent"] = Relationship(
        back_populates="brand",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[SponsoredContent.brand_id]"},
    )
    premium_purchases: List["PremiumFeaturePurchase"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # Stories relationships
    story_highlights: List["StoryHighlight"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # Live streams relationships
    live_streams: List["Stream"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # User profile relationships
    profile: Optional["Profile"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    profile_views: List["ProfileView"] = Relationship(
        back_populates="viewer", cascade_delete=True
    )

    # Verification relationships
    verification_requests: List["VerificationRequest"] = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[VerificationRequest.user_id]"},
    )
    reviewed_requests: List["VerificationRequest"] = Relationship(
        back_populates="reviewer",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[VerificationRequest.reviewed_by]"},
    )
    verification_badges: List["VerificationBadge"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # Notification relationships
    received_notifications: List["Notification"] = Relationship(
        back_populates="recipient",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[Notification.recipient_id]"},
    )
    sent_notifications: List["Notification"] = Relationship(
        back_populates="sender",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[Notification.sender_id]"},
    )

    # Device relationships
    devices: List["Device"] = Relationship(back_populates="user", cascade_delete=True)

    # Notification preference relationships
    notification_preferences: Optional["NotificationPreference"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    # Search relationships
    search_queries: List["SearchQuery"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    search_history: List["SearchHistory"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
