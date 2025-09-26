import enum


class StreamStatus(str, enum.Enum):
    scheduled = "scheduled"
    live = "live"
    ended = "ended"
    cancelled = "cancelled"


class StreamVisibility(str, enum.Enum):
    public = "public"
    private = "private"
    unlisted = "unlisted"


class StreamQuality(str, enum.Enum):
    low = "480p"
    medium = "720p"
    high = "1080p"
    ultra = "4k"


class ViewerRole(str, enum.Enum):
    viewer = "viewer"
    moderator = "moderator"
    host = "host"


class BadgeType(str, enum.Enum):
    """Badge types for donations/tips"""

    heart = "heart"
    star = "star"
    diamond = "diamond"
    fire = "fire"
    rocket = "rocket"
    crown = "crown"
