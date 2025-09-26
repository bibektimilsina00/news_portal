import enum


class StreamStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    ENDED = "ended"
    CANCELLED = "cancelled"


class StreamVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class StreamQuality(str, enum.Enum):
    LOW = "480p"
    MEDIUM = "720p"
    HIGH = "1080p"
    ULTRA = "4k"


class ViewerRole(str, enum.Enum):
    VIEWER = "viewer"
    MODERATOR = "moderator"
    HOST = "host"


class BadgeType(str, enum.Enum):
    """Badge types for donations/tips"""

    HEART = "heart"
    STAR = "star"
    DIAMOND = "diamond"
    FIRE = "fire"
    ROCKET = "rocket"
    CROWN = "crown"
