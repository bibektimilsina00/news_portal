import enum


class ReelType(str, enum.Enum):
    ORIGINAL = "original"
    DUET = "duet"
    STITCH = "stitch"
    REMIX = "remix"


class ReelStatus(str, enum.Enum):
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class ReelVisibility(str, enum.Enum):
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"


class EffectType(str, enum.Enum):
    FILTER = "filter"
    TRANSITION = "transition"
    TEXT = "text"
    STICKER = "sticker"
    GREEN_SCREEN = "green_screen"
    SPEED = "speed"
    AUDIO = "audio"


class EffectCategory(str, enum.Enum):
    VISUAL = "visual"
    AUDIO = "audio"
    TEXT = "text"
    TRANSITION = "transition"
