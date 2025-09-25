import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, func, or_
from sqlmodel import Session, case, select

from app.core.config import settings
from app.modules.posts.model.post import Post, PostStatus, PostType, PostVisibility
from app.modules.posts.schema.post import PostCreate, PostFilter, PostUpdate
from app.shared.crud.base import CRUDBase


class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    """CRUD operations for posts"""

    def get_published_posts(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[uuid.UUID] = None,
        post_type: Optional[PostType] = None,
        visibility: Optional[PostVisibility] = None,
    ) -> List[Post]:
        """Get published posts with optional filtering"""
        statement = select(Post).where(Post.status == PostStatus.PUBLISHED)

        if user_id:
            statement = statement.where(Post.user_id == user_id)

        if post_type:
            statement = statement.where(Post.post_type == post_type)

        if visibility:
            statement = statement.where(Post.visibility == visibility)

        statement = statement.order_by(Post.published_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_posts_by_user(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PostStatus] = None,
        visibility: Optional[PostVisibility] = None,
    ) -> List[Post]:
        """Get posts by user"""
        statement = select(Post).where(Post.user_id == user_id)

        if status:
            statement = statement.where(Post.status == status)

        if visibility:
            statement = statement.where(Post.visibility == visibility)

        statement = statement.order_by(Post.created_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_feed_posts(
        self,
        session: Session,
        *,
        user_ids: List[uuid.UUID],
        skip: int = 0,
        limit: int = 100,
        include_private: bool = False,
    ) -> List[Post]:
        """Get posts for user feed"""
        statement = select(Post).where(
            and_(Post.user_id.in_(user_ids), Post.status == PostStatus.PUBLISHED)
        )

        if not include_private:
            statement = statement.where(Post.visibility == PostVisibility.PUBLIC)

        statement = statement.order_by(Post.published_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_explore_posts(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        exclude_user_id: Optional[uuid.UUID] = None,
    ) -> List[Post]:
        """Get posts for explore/discover page"""
        statement = select(Post).where(Post.status == PostStatus.PUBLISHED)

        if exclude_user_id:
            statement = statement.where(Post.user_id != exclude_user_id)

        statement = statement.where(Post.visibility == PostVisibility.PUBLIC)

        # Order by engagement (likes + comments + shares)
        statement = statement.order_by(
            (Post.like_count + Post.comment_count * 2 + Post.share_count * 3).desc()
        )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_posts_with_media(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[uuid.UUID] = None,
    ) -> List[Post]:
        """Get posts that have media"""
        statement = select(Post).where(
            and_(Post.status == PostStatus.PUBLISHED, Post.media_urls != [])
        )

        if user_id:
            statement = statement.where(Post.user_id == user_id)

        statement = statement.order_by(Post.created_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_posts_by_location(
        self,
        session: Session,
        *,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Post]:
        """Get posts near a location"""
        # Simplified location-based query
        # In production, use PostGIS or similar for proper geospatial queries

        lat_range = radius_km / 111.0  # 1 degree latitude ≈ 111 km
        lon_range = radius_km / (111.0 * abs(latitude))  # Adjust for longitude

        statement = (
            select(Post)
            .where(
                and_(
                    Post.status == PostStatus.PUBLISHED,
                    Post.latitude.isnot(None),
                    Post.longitude.isnot(None),
                    Post.latitude >= latitude - lat_range,
                    Post.latitude <= latitude + lat_range,
                    Post.longitude >= longitude - lon_range,
                    Post.longitude <= longitude + lon_range,
                )
            )
            .order_by(Post.created_at.desc())
        )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def search_posts(
        self,
        session: Session,
        *,
        query: str,
        skip: int = 0,
        limit: int = 50,
        only_published: bool = True,
    ) -> List[Post]:
        """Search posts by caption or content"""
        search_term = f"%{query}%"

        statement = select(Post).where(
            or_(Post.caption.ilike(search_term), Post.content.ilike(search_term))
        )

        if only_published:
            statement = statement.where(Post.status == PostStatus.PUBLISHED)

        statement = statement.order_by(Post.created_at.desc())
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_highlighted_posts(
        self, session: Session, *, skip: int = 0, limit: int = 20
    ) -> List[Post]:
        """Get highlighted/story posts"""
        statement = (
            select(Post)
            .where(
                and_(Post.status == PostStatus.PUBLISHED, Post.is_highlighted == True)
            )
            .order_by(Post.created_at.desc())
        )

        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_pinned_posts(self, session: Session, *, user_id: uuid.UUID) -> List[Post]:
        """Get user's pinned posts"""
        statement = (
            select(Post)
            .where(
                and_(
                    Post.user_id == user_id,
                    Post.is_pinned == True,
                    Post.status == PostStatus.PUBLISHED,
                )
            )
            .order_by(Post.created_at.desc())
        )

        return list(session.exec(statement))

    def get_draft_posts(self, session: Session, *, user_id: uuid.UUID) -> List[Post]:
        """Get user's draft posts"""
        statement = (
            select(Post)
            .where(and_(Post.user_id == user_id, Post.status == PostStatus.DRAFT))
            .order_by(Post.created_at.desc())
        )

        return list(session.exec(statement))

    def get_scheduled_posts(
        self, session: Session, *, user_id: uuid.UUID
    ) -> List[Post]:
        """Get user's scheduled posts"""
        statement = (
            select(Post)
            .where(
                and_(
                    Post.user_id == user_id,
                    Post.status == PostStatus.SCHEDULED,
                    Post.scheduled_at > datetime.utcnow(),
                )
            )
            .order_by(Post.scheduled_at.asc())
        )

        return list(session.exec(statement))

    def update_engagement_metrics(
        self, session: Session, *, post_id: uuid.UUID
    ) -> Optional[Post]:
        """Update engagement metrics for post"""
        post = self.get(session=session, id=post_id)
        if not post:
            return None

        # Update last interaction time
        post.last_interaction_at = datetime.utcnow()

        session.add(post)
        session.commit()
        session.refresh(post)

        return post

    def schedule_post(
        self, session: Session, *, post_id: uuid.UUID, scheduled_at: datetime
    ) -> Optional[Post]:
        """Schedule post for future publication"""
        post = self.get(session=session, id=post_id)
        if not post:
            return None

        post.status = PostStatus.SCHEDULED
        post.scheduled_at = scheduled_at

        session.add(post)
        session.commit()
        session.refresh(post)

        return post

    def publish_post(self, session: Session, *, post_id: uuid.UUID) -> Optional[Post]:
        """Publish post"""
        post = self.get(session=session, id=post_id)
        if not post:
            return None

        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.utcnow()
        post.last_interaction_at = datetime.utcnow()

        session.add(post)
        session.commit()
        session.refresh(post)

        return post

    def archive_post(self, session: Session, *, post_id: uuid.UUID) -> Optional[Post]:
        """Archive post"""
        post = self.get(session=session, id=post_id)
        if not post:
            return None

        post.status = PostStatus.ARCHIVED

        session.add(post)
        session.commit()
        session.refresh(post)

        return post

    def get_posts_stats(
        self, session: Session, *, user_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Get posts statistics"""
        base_query = select(Post)

        if user_id:
            base_query = base_query.where(Post.user_id == user_id)

        # Total posts
        total_posts = session.exec(
            select(func.count(Post.id)).select_from(base_query)
        ).one()

        # By status
        published_count = session.exec(
            select(func.count(Post.id))
            .select_from(base_query)
            .where(Post.status == PostStatus.PUBLISHED)
        ).one()

        draft_count = session.exec(
            select(func.count(Post.id))
            .select_from(base_query)
            .where(Post.status == PostStatus.DRAFT)
        ).one()

        scheduled_count = session.exec(
            select(func.count(Post.id))
            .select_from(base_query)
            .where(Post.status == PostStatus.SCHEDULED)
        ).one()

        # With media
        media_count = session.exec(
            select(func.count(Post.id))
            .select_from(base_query)
            .where(Post.media_urls != [])
        ).one()

        # With location
        location_count = session.exec(
            select(func.count(Post.id))
            .select_from(base_query)
            .where(Post.latitude.isnot(None))
        ).one()

        return {
            "total_posts": total_posts,
            "published_posts": published_count,
            "draft_posts": draft_count,
            "scheduled_posts": scheduled_count,
            "posts_with_media": media_count,
            "posts_with_location": location_count,
        }

    def get_user_feed(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        following_ids: List[uuid.UUID],
        skip: int = 0,
        limit: int = 100,
    ) -> List[Post]:
        """Get personalized user feed"""
        # Get posts from users they follow
        statement = (
            select(Post)
            .where(
                and_(
                    Post.user_id.in_(following_ids),
                    Post.status == PostStatus.PUBLISHED,
                    Post.visibility == PostVisibility.PUBLIC,
                )
            )
            .order_by(Post.created_at.desc())
        )

        return list(session.exec(statement.offset(skip).limit(limit)))


# Create singleton instance
post = CRUDPost(Post)
