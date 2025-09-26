import enum


class StoryType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"
    TEXT = "text"


class StoryStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DELETED = "deleted"


class StoryVisibility(str, enum.Enum):
    PUBLIC = "public"
    CLOSE_FRIENDS = "close_friends"
    PRIVATE = "private"


class InteractionType(str, enum.Enum):
    POLL_VOTE = "poll_vote"
    QUESTION_REPLY = "question_reply"
    QUIZ_ANSWER = "quiz_answer"
    REACTION = "reaction"
