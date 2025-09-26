# User Management
# AI Features Module
from app.modules.ai_features.model.ai_features import (
    AIModelMetrics,
    AnomalyDetection,
    ChurnPrediction,
    ContentAnalysis,
    ContentClassification,
    ContentRecommendation,
    EngagementPrediction,
    PersonalizedFeed,
    TranslationCache,
    TrendAnalysis,
    UserBehavior,
)

# Analytics Module
from app.modules.analytics.model.analytics import (
    ContentAnalytics,
    PlatformAnalytics,
    UserAnalytics,
)

# Content Moderation Module
from app.modules.content_moderation.model.moderation import (
    BanAppeal,
    ContentFlag,
    ContentReport,
    ModerationAction,
    ModerationAppeal,
    ModerationLog,
    ModerationRule,
    UserBan,
    UserStrike,
)

# Integrations Module
from app.modules.integrations.model.integrations import (
    APIKey,
    APIRequestLog,
    ExternalNewsArticle,
    Integration,
    IntegrationNewsSource,
    IntegrationSyncLog,
    SocialMediaPost,
    SportsData,
    StockData,
    WeatherData,
    Webhook,
    WebhookDelivery,
)
from app.modules.live_streams.model.badge import StreamBadge

# Live Streams Module
from app.modules.live_streams.model.stream import Stream
from app.modules.live_streams.model.viewer import StreamViewer

# Media Module
from app.modules.media.model.media import (
    MediaAnalytics,
    MediaFile,
    MediaProcessingJob,
    MediaStorage,
)

# Messaging Module
from app.modules.messaging.model.conversation import Conversation
from app.modules.messaging.model.message import Message
from app.modules.messaging.model.participant import ConversationParticipant

# Monetization Module
from app.modules.monetization.model.monetization import (
    AdCampaign,
    CreatorEarning,
    CreatorPayout,
    Payment,
    PremiumFeature,
    SponsoredContent,
    SubscriptionTier,
    UserSubscription,
)
from app.modules.news.model.category import Category
from app.modules.news.model.factcheck import FactCheck

# News Module
from app.modules.news.model.news import News, NewsRelated, NewsTag
from app.modules.news.model.source import NewsSource, NewsSourceFollow
from app.modules.notifications.model.device import Device

# Notifications Module
from app.modules.notifications.model.notification import Notification
from app.modules.notifications.model.preference import NotificationPreference

# Posts Module
from app.modules.posts.model.post import Post
from app.modules.reels.model.effect import Effect
from app.modules.reels.model.music import Music

# Reels Module
from app.modules.reels.model.reel import Reel
from app.modules.search.model.history import SearchHistory

# Search Module
from app.modules.search.model.search import SearchQuery, SearchResult
from app.modules.search.model.trending import TrendingTopic
from app.modules.stories.model.highlight import StoryHighlight
from app.modules.stories.model.interaction import StoryInteraction

# Stories Module
from app.modules.stories.model.story import Story
from app.modules.stories.model.viewer import StoryViewer
from app.modules.users.model.user import User
