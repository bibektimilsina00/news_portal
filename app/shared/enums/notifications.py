import enum


class NotificationType(str, enum.Enum):
    like = "like"
    comment = "comment"
    follow = "follow"
    mention = "mention"
    share = "share"
    message = "message"
    news_published = "news_published"
    story_added = "story_added"
    reel_published = "reel_published"
    live_stream_started = "live_stream_started"
    system = "system"


class NotificationPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    read = "read"
    failed = "failed"


class DeviceType(str, enum.Enum):
    ios = "ios"
    android = "android"
    web = "web"
    desktop = "desktop"


class DeviceStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
