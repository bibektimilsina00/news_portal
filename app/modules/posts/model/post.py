import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Enum, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.posts.model.bookmark import Bookmark
    from app.modules.posts.model.comment import Comment
    from app.modules.posts.model.like import Like
    from app.modules.posts.model.media import PostMedia
    from app.modules.posts.model.post_tag import PostTag
    from app.modules.posts.model.tag import Tag
    from app.modules.users.model.user import User


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


class Post(SQLModel, table=True):
    """User posts model for Instagram-style platform"""

    __tablename__ = "posts"

    # Primary Key
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    # Foreign Keys
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Content Fields
    caption: Optional[str] = Field(default=None, max_length=2200)
    content: Optional[str] = Field(default=None)
    summary: Optional[str] = Field(default=None, max_length=500)

    # Post Type & Status
    post_type: PostType = Field(default=PostType.REGULAR, index=True)
    status: PostStatus = Field(default=PostStatus.DRAFT, index=True)
    visibility: PostVisibility = Field(default=PostVisibility.PUBLIC)

    # Media Fields
    media_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    cover_image_url: Optional[str] = Field(default=None, max_length=500)

    # Location Data
    location_name: Optional[str] = Field(default=None, max_length=255)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # Engagement Metrics
    like_count: int = Field(default=0)
    comment_count: int = Field(default=0)
    share_count: int = Field(default=0)
    bookmark_count: int = Field(default=0)
    view_count: int = Field(default=0)

    # Social Metrics
    facebook_shares: int = Field(default=0)
    twitter_shares: int = Field(default=0)
    linkedin_shares: int = Field(default=0)
    whatsapp_shares: int = Field(default=0)

    # Instagram-style Features
    is_sensitive: bool = Field(default=False)
    is_highlighted: bool = Field(default=False)
    is_pinned: bool = Field(default=False)

    # News-specific (if applicable)
    is_breaking_news: bool = Field(default=False)
    fact_check_status: str = Field(default="pending", max_length=50)

    # Scheduling
    scheduled_at: Optional[datetime] = Field(default=None, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None, index=True)
    last_interaction_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    owner: "User" = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post", cascade_delete=True)
    likes: List["Like"] = Relationship(back_populates="post", cascade_delete=True)
    bookmarks: List["Bookmark"] = Relationship(
        back_populates="post", cascade_delete=True
    )
    post_tags: List["PostTag"] = Relationship(
        back_populates="post", cascade_delete=True
    )
    media_items: List["PostMedia"] = Relationship(
        back_populates="post", cascade_delete=True
    )

    class Config:
        orm_mode = True

    def increment_like_count(self) -> None:
        """Increment like count"""
        self.like_count += 1
        self.last_interaction_at = datetime.utcnow()

    def decrement_like_count(self) -> None:
        """Decrement like count"""
        if self.like_count > 0:
            self.like_count -= 1
            self.last_interaction_at = datetime.utcnow()

    def increment_comment_count(self) -> None:
        """Increment comment count"""
        self.comment_count += 1
        self.last_interaction_at = datetime.utcnow()

    def decrement_comment_count(self) -> None:
        """Decrement comment count"""
        if self.comment_count > 0:
            self.comment_count -= 1
            self.last_interaction_at = datetime.utcnow()

    def increment_share_count(self) -> None:
        """Increment share count"""
        self.share_count += 1
        self.last_interaction_at = datetime.utcnow()

    def increment_bookmark_count(self) -> None:
        """Increment bookmark count"""
        self.bookmark_count += 1
        self.last_interaction_at = datetime.utcnow()

    def decrement_bookmark_count(self) -> None:
        """Decrement bookmark count"""
        if self.bookmark_count > 0:
            self.bookmark_count -= 1
            self.last_interaction_at = datetime.utcnow()

    def increment_view_count(self) -> None:
        """Increment view count"""
        self.view_count += 1
        self.last_interaction_at = datetime.utcnow()

    def is_published(self) -> bool:
        """Check if post is published"""
        return self.status == PostStatus.PUBLISHED

    def is_visible_to_user(
        self,
        user_id: uuid.UUID,
        is_following: bool = False,
        is_close_friend: bool = False,
    ) -> bool:
        """Check if post is visible to specific user"""
        if self.visibility == PostVisibility.PUBLIC:
            return True
        elif self.visibility == PostVisibility.FOLLOWERS_ONLY:
            return is_following
        elif self.visibility == PostVisibility.CLOSE_FRIENDS:
            return is_close_friend
        return False

    def get_share_url(self) -> str:
        """Generate share URL"""
        return f"{settings.FRONTEND_URL}/post/{self.id}"


class PostMedia(SQLModel, table=True):
    """Media attachments for posts"""

    __tablename__ = "post_media"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    post_id: uuid.UUID = Field(foreign_key="posts.id", index=True)

    # Media Details
    media_type: str = Field(max_length=50)  # image, video, audio, document
    media_url: str = Field(max_length=1000)
    thumbnail_url: Optional[str] = Field(default=None, max_length=1000)

    # Media Metadata
    file_name: Optional[str] = Field(default=None, max_length=255)
    file_size: Optional[int] = Field(default=None)
    mime_type: Optional[str] = Field(default=None, max_length=100)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    duration: Optional[float] = Field(default=None)  # For video/audio in seconds

    # Processing Status
    is_processed: bool = Field(default=False)
    processing_error: Optional[str] = Field(default=None)

    # Order & Display
    sort_order: int = Field(default=0)
    alt_text: Optional[str] = Field(default=None, max_length=500)
    caption: Optional[str] = Field(default=None, max_length=1000)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    post: "Post" = Relationship(back_populates="media_items")

    class Config:
        orm_mode = True
