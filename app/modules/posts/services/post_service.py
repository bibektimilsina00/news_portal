import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Session

from app.modules.posts.crud.crud_post import post
from app.modules.posts.model.post import Post, PostStatus
from app.modules.posts.schema.post import PostCreate, PostUpdate
from app.shared.exceptions.exceptions import (
    InvalidPostDataException,
    PostNotFoundException,
    UnauthorizedException,
)


class PostService:
    """Service layer for post management"""

    @staticmethod
    def create_post(*, session: Session, post_create: PostCreate) -> Post:
        """Create new post"""
        # Validate post data
        if (
            not post_create.caption
            and not post_create.content
            and not post_create.media_urls
        ):
            raise InvalidPostDataException("Post must have caption, content, or media")

        # Generate slug if title/caption exists
        if post_create.caption and not post_create.slug:
            post_create.slug = post_create.caption[:50].lower().replace(" ", "-")

        return post.create(session=session, obj_in=post_create)

    @staticmethod
    def get_post(*, session: Session, post_id: uuid.UUID) -> Post:
        """Get post by ID"""
        db_post = post.get(session=session, id=post_id)
        if not db_post:
            raise PostNotFoundException("Post not found")
        return db_post

    @staticmethod
    def get_post_by_user(
        *, session: Session, user_id: uuid.UUID, post_id: uuid.UUID
    ) -> Post:
        """Get user's post"""
        db_post = post.get(session=session, id=post_id)
        if not db_post:
            raise PostNotFoundException("Post not found")

        if db_post.user_id != user_id:
            raise UnauthorizedException("Post does not belong to user")

        return db_post

    @staticmethod
    def get_posts_by_user(
        *,
        session: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PostStatus] = None,
    ) -> List[Post]:
        """Get posts by user"""
        return post.get_posts_by_user(
            session=session, user_id=user_id, skip=skip, limit=limit, status=status
        )

    @staticmethod
    def get_published_posts(
        *,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[uuid.UUID] = None,
    ) -> List[Post]:
        """Get published posts"""
        return post.get_published_posts(
            session=session, skip=skip, limit=limit, user_id=user_id
        )

    @staticmethod
    def get_user_feed(
        *,
        session: Session,
        user_id: uuid.UUID,
        following_ids: List[uuid.UUID],
        skip: int = 0,
        limit: int = 100,
    ) -> List[Post]:
        """Get personalized user feed"""
        return post.get_user_feed(
            session=session,
            user_id=user_id,
            following_ids=following_ids,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def get_explore_posts(
        *,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        exclude_user_id: Optional[uuid.UUID] = None,
    ) -> List[Post]:
        """Get posts for explore/discover page"""
        return post.get_explore_posts(
            session=session, skip=skip, limit=limit, exclude_user_id=exclude_user_id
        )

    @staticmethod
    def update_post(
        *, session: Session, post_id: uuid.UUID, user_id: uuid.UUID, post_in: PostUpdate
    ) -> Post:
        """Update post (user must own the post)"""
        db_post = PostService.get_post_by_user(
            session=session, user_id=user_id, post_id=post_id
        )

        return post.update(session=session, db_obj=db_post, obj_in=post_in)

    @staticmethod
    def delete_post(
        *, session: Session, post_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Delete post (user must own the post)"""
        db_post = PostService.get_post_by_user(
            session=session, user_id=user_id, post_id=post_id
        )

        return post.remove(session=session, id=post_id)

    @staticmethod
    def publish_post(
        *, session: Session, post_id: uuid.UUID, user_id: uuid.UUID
    ) -> Post:
        """Publish user's post"""
        db_post = PostService.get_post_by_user(
            session=session, user_id=user_id, post_id=post_id
        )

        if db_post.status != PostStatus.draft:
            raise InvalidPostDataException("Only draft posts can be published")

        return post.publish_post(session=session, post_id=post_id)

    @staticmethod
    def schedule_post(
        *,
        session: Session,
        post_id: uuid.UUID,
        user_id: uuid.UUID,
        scheduled_at: datetime,
    ) -> Post:
        """Schedule post for future publication"""
        db_post = PostService.get_post_by_user(
            session=session, user_id=user_id, post_id=post_id
        )

        if scheduled_at <= datetime.utcnow():
            raise InvalidPostDataException("Scheduled time must be in the future")

        return post.schedule_post(
            session=session, post_id=post_id, scheduled_at=scheduled_at
        )

    @staticmethod
    def search_posts(
        *, session: Session, query: str, skip: int = 0, limit: int = 50
    ) -> List[Post]:
        """Search posts by caption or content"""
        return post.search_posts(session=session, query=query, skip=skip, limit=limit)

    @staticmethod
    def get_posts_with_media(
        *,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[uuid.UUID] = None,
    ) -> List[Post]:
        """Get posts that have media"""
        return post.get_posts_with_media(
            session=session, skip=skip, limit=limit, user_id=user_id
        )

    @staticmethod
    def get_posts_by_location(
        *,
        session: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Post]:
        """Get posts near a location"""
        return post.get_posts_by_location(
            session=session,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def get_highlighted_posts(
        *, session: Session, skip: int = 0, limit: int = 20
    ) -> List[Post]:
        """Get highlighted posts"""
        return post.get_highlighted_posts(session=session, skip=skip, limit=limit)

    @staticmethod
    def get_pinned_posts(*, session: Session, user_id: uuid.UUID) -> List[Post]:
        """Get user's pinned posts"""
        return post.get_pinned_posts(session=session, user_id=user_id)

    @staticmethod
    def get_draft_posts(*, session: Session, user_id: uuid.UUID) -> List[Post]:
        """Get user's draft posts"""
        return post.get_draft_posts(session=session, user_id=user_id)

    @staticmethod
    def get_scheduled_posts(*, session: Session, user_id: uuid.UUID) -> List[Post]:
        """Get user's scheduled posts"""
        return post.get_scheduled_posts(session=session, user_id=user_id)

    @staticmethod
    def pin_post(*, session: Session, post_id: uuid.UUID, user_id: uuid.UUID) -> Post:
        """Pin a post"""
        db_post = PostService.get_post_by_user(
            session=session, user_id=user_id, post_id=post_id
        )

        return post.update(session=session, db_obj=db_post, obj_in={"is_pinned": True})

    @staticmethod
    def unpin_post(*, session: Session, post_id: uuid.UUID, user_id: uuid.UUID) -> Post:
        """Unpin a post"""
        db_post = PostService.get_post_by_user(
            session=session, user_id=user_id, post_id=post_id
        )

        return post.update(session=session, db_obj=db_post, obj_in={"is_pinned": False})

    @staticmethod
    def highlight_post(
        *, session: Session, post_id: uuid.UUID, user_id: uuid.UUID
    ) -> Post:
        """Highlight a post"""
        db_post = PostService.get_post_by_user(
            session=session, user_id=user_id, post_id=post_id
        )

        return post.update(
            session=session, db_obj=db_post, obj_in={"is_highlighted": True}
        )

    @staticmethod
    def remove_highlight(
        *, session: Session, post_id: uuid.UUID, user_id: uuid.UUID
    ) -> Post:
        """Remove highlight from post"""
        db_post = PostService.get_post_by_user(
            session=session, user_id=user_id, post_id=post_id
        )

        return post.update(
            session=session, db_obj=db_post, obj_in={"is_highlighted": False}
        )

    @staticmethod
    def update_engagement_metrics(
        *, session: Session, post_id: uuid.UUID
    ) -> Optional[Post]:
        """Update engagement metrics for post"""
        return post.update_engagement_metrics(session=session, post_id=post_id)

    @staticmethod
    def get_posts_stats(
        *, session: Session, user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get posts statistics"""
        return post.get_posts_stats(session=session, user_id=user_id)

    @staticmethod
    def is_post_visible_to_user(
        *,
        post: Post,
        user_id: uuid.UUID,
        is_following: bool = False,
        is_close_friend: bool = False,
    ) -> bool:
        """Check if post is visible to specific user"""
        return post.is_visible_to_user(
            user_id=user_id, is_following=is_following, is_close_friend=is_close_friend
        )


# Create singleton instance
post_service = PostService()
