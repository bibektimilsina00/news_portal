import enum


class PostType(str, enum.Enum):
    regular = "regular"
    story = "story"
    reel = "reel"
    live = "live"
    article = "article"


class PostStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"
    scheduled = "scheduled"


class PostVisibility(str, enum.Enum):
    public = "public"
    followers_only = "followers_only"
    close_friends = "close_friends"
