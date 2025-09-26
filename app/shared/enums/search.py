import enum


class SearchType(str, enum.Enum):
    POST = "post"
    NEWS = "news"
    USER = "user"
    HASHTAG = "hashtag"
    LOCATION = "location"
    STORY = "story"
    REEL = "reel"
    LIVE_STREAM = "live_stream"


class SearchResultType(str, enum.Enum):
    CONTENT = "content"
    USER = "user"
    HASHTAG = "hashtag"
    LOCATION = "location"
    TRENDING = "trending"
