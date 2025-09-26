import enum


class IntegrationType(str, enum.Enum):
    social_media = "social_media"
    news_api = "news_api"
    weather = "weather"
    stocks = "stocks"
    sports = "sports"
    payment = "payment"
    maps = "maps"
    calendar = "calendar"
    email = "email"
    sms = "sms"
    webhook = "webhook"


class IntegrationStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    error = "error"
    pending = "pending"
    suspended = "suspended"


class WebhookEvent(str, enum.Enum):
    post_created = "post.created"
    post_updated = "post.updated"
    post_deleted = "post.deleted"
    user_registered = "user.registered"
    user_updated = "user.updated"
    comment_added = "comment.added"
    like_added = "like.added"
    follow_added = "follow.added"
