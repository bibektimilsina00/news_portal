import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.modules.stories.model.interaction import InteractionType


# Base Schemas
class StoryInteractionBase(SQLModel):
    """Base story interaction schema"""

    interaction_type: InteractionType
    content: Optional[str] = Field(default=None, max_length=1000)
    option_selected: Optional[str] = Field(default=None, max_length=255)
    is_correct: Optional[bool] = Field(default=None)
    interaction_metadata: Optional[Dict[str, Any]] = Field(default=None)


class StoryInteractionCreate(StoryInteractionBase):
    """Schema for creating a new story interaction"""

    story_id: uuid.UUID


class StoryInteractionUpdate(SQLModel):
    """Schema for updating an existing story interaction"""

    content: Optional[str] = Field(default=None, max_length=1000)
    option_selected: Optional[str] = Field(default=None, max_length=255)
    interaction_metadata: Optional[Dict[str, Any]] = Field(default=None)


class StoryInteractionPublic(StoryInteractionBase):
    """Public story interaction schema"""

    id: uuid.UUID
    story_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class StoryInteractionWithUser(StoryInteractionPublic):
    """Story interaction with user information"""

    # user: UserPublic  # TODO: Add when user schemas are available
    pass


class StoryInteractionList(SQLModel):
    """Schema for story interaction list responses"""

    interactions: List[StoryInteractionPublic]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


# Poll response schemas
class PollVoteCreate(BaseModel):
    """Schema for creating a poll vote"""

    story_id: uuid.UUID
    option_selected: str = Field(min_length=1, max_length=255)


class PollResults(BaseModel):
    """Schema for poll results"""

    total_votes: int
    options: Dict[str, int]  # option -> vote count


# Question response schemas
class QuestionReplyCreate(BaseModel):
    """Schema for creating a question reply"""

    story_id: uuid.UUID
    content: str = Field(min_length=1, max_length=1000)


class QuestionReplies(BaseModel):
    """Schema for question replies"""

    replies: List[StoryInteractionPublic]
    total_replies: int


# Quiz response schemas
class QuizAnswerCreate(BaseModel):
    """Schema for submitting a quiz answer"""

    story_id: uuid.UUID
    option_selected: str = Field(min_length=1, max_length=255)


class QuizResult(BaseModel):
    """Schema for quiz result"""

    is_correct: bool
    explanation: Optional[str] = None
    correct_option: Optional[str] = None
