import enum


class PostType(str, enum.Enum):
    REGULAR = "regular"
    STORY = "story"
    REEL = "reel"
    LIVE = "live"
    ARTICLE = "article"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"


class PostVisibility(str, enum.Enum):
    PUBLIC = "public"
    FOLLOWERS_ONLY = "followers_only"
    CLOSE_FRIENDS = "close_friends"
