import enum


class SearchType(str, enum.Enum):
    post = "post"
    news = "news"
    user = "user"
    hashtag = "hashtag"
    location = "location"
    story = "story"
    reel = "reel"
    live_stream = "live_stream"


class SearchResultType(str, enum.Enum):
    content = "content"
    user = "user"
    hashtag = "hashtag"
    location = "location"
    trending = "trending"
