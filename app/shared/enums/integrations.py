import enum


class IntegrationType(str, enum.Enum):
    SOCIAL_MEDIA = "social_media"
    NEWS_API = "news_api"
    WEATHER = "weather"
    STOCKS = "stocks"
    SPORTS = "sports"
    PAYMENT = "payment"
    MAPS = "maps"
    CALENDAR = "calendar"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class IntegrationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    SUSPENDED = "suspended"


class WebhookEvent(str, enum.Enum):
    POST_CREATED = "post.created"
    POST_UPDATED = "post.updated"
    POST_DELETED = "post.deleted"
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    COMMENT_ADDED = "comment.added"
    LIKE_ADDED = "like.added"
    FOLLOW_ADDED = "follow.added"
