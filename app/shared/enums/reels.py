import enum


class ReelType(str, enum.Enum):
    original = "original"
    duet = "duet"
    stitch = "stitch"
    remix = "remix"


class ReelStatus(str, enum.Enum):
    processing = "processing"
    published = "published"
    failed = "failed"
    deleted = "deleted"


class ReelVisibility(str, enum.Enum):
    public = "public"
    friends = "friends"
    private = "private"


class EffectType(str, enum.Enum):
    filter = "filter"
    transition = "transition"
    text = "text"
    sticker = "sticker"
    green_screen = "green_screen"
    speed = "speed"
    audio = "audio"


class EffectCategory(str, enum.Enum):
    visual = "visual"
    audio = "audio"
    text = "text"
    transition = "transition"
