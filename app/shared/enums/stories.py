import enum


class StoryType(str, enum.Enum):
    photo = "photo"
    video = "video"
    text = "text"


class StoryStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    deleted = "deleted"


class StoryVisibility(str, enum.Enum):
    public = "public"
    close_friends = "close_friends"
    private = "private"


class InteractionType(str, enum.Enum):
    poll_vote = "poll_vote"
    question_reply = "question_reply"
    quiz_answer = "quiz_answer"
    reaction = "reaction"
