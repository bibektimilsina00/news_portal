import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.stories.model.story import Story
    from app.modules.users.model.user import User


class InteractionType(str, enum.Enum):
    POLL_VOTE = "poll_vote"
    QUESTION_REPLY = "question_reply"
    QUIZ_ANSWER = "quiz_answer"
    REACTION = "reaction"


class StoryInteraction(SQLModel, table=True):
    """Interactive elements for stories (polls, questions, quizzes)"""


    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    story_id: uuid.UUID = Field(foreign_key="story.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Interaction details
    interaction_type: InteractionType = Field(index=True)
    content: Optional[str] = Field(default=None, max_length=1000)  # reply text, etc.

    # For polls and quizzes
    option_selected: Optional[str] = Field(default=None, max_length=255)
    is_correct: Optional[bool] = Field(default=None)  # for quiz answers

    # Additional metadata
    interaction_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    story: "Story" = Relationship(back_populates="interactions")
    user: "User" = Relationship()
