import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from app.modules.users.crud.crud_profile import close_friend, profile, user_block
from app.modules.users.model.profile import CloseFriend, Profile, UserBlock
from app.modules.users.schema.profile import ProfileCreate, ProfileUpdate
from app.shared.deps.deps import SessionDep


class ProfileService:
    """Service layer for profile operations"""

    @staticmethod
    def get_user_profile(
        session: SessionDep, *, user_id: uuid.UUID
    ) -> Optional[Profile]:
        """Get user profile by user ID"""
        return profile.get_by_user_id(session=session, user_id=user_id)

    @staticmethod
    def create_or_update_profile(
        session: SessionDep, *, user_id: uuid.UUID, profile_data: ProfileCreate
    ) -> Profile:
        """Create or update user profile"""
        existing_profile = profile.get_by_user_id(session=session, user_id=user_id)

        if existing_profile:
            # Update existing profile
            return profile.update_profile(
                session=session,
                profile=existing_profile,
                update_data=profile_data.model_dump(exclude_unset=True),
            )
        else:
            # Create new profile
            return profile.create_profile_for_user(
                session=session, user_id=user_id, profile_data=profile_data.model_dump()
            )

    @staticmethod
    def update_profile(
        session: SessionDep, *, user_id: uuid.UUID, profile_data: ProfileUpdate
    ) -> Optional[Profile]:
        """Update user profile"""
        existing_profile = profile.get_by_user_id(session=session, user_id=user_id)
        if not existing_profile:
            return None

        return profile.update_profile(
            session=session,
            profile=existing_profile,
            update_data=profile_data.model_dump(exclude_unset=True),
        )

    @staticmethod
    def add_close_friend(
        session: SessionDep, *, user_id: uuid.UUID, friend_id: uuid.UUID
    ) -> CloseFriend:
        """Add a user to close friends list"""
        # Check if user is trying to add themselves
        if user_id == friend_id:
            raise ValueError("Cannot add yourself to close friends")

        # Try to add - method will return existing if already friends
        result = close_friend.add_close_friend(
            session=session, user_id=user_id, friend_id=friend_id
        )
        return result

    @staticmethod
    def remove_close_friend(
        session: SessionDep, *, user_id: uuid.UUID, friend_id: uuid.UUID
    ) -> bool:
        """Remove a user from close friends list"""
        return close_friend.remove_close_friend(
            session=session, user_id=user_id, friend_id=friend_id
        )

    @staticmethod
    def get_close_friends(
        session: SessionDep, *, user_id: uuid.UUID
    ) -> List[CloseFriend]:
        """Get user's close friends"""
        return close_friend.get_close_friends(session=session, user_id=user_id)

    @staticmethod
    def block_user(
        session: SessionDep, *, blocker_id: uuid.UUID, blocked_id: uuid.UUID
    ) -> UserBlock:
        """Block a user"""
        # Check if already blocked
        if user_block.is_blocked(
            session=session, blocker_id=blocker_id, blocked_id=blocked_id
        ):
            raise ValueError("User is already blocked")

        return user_block.block_user(
            session=session, blocker_id=blocker_id, blocked_id=blocked_id
        )

    @staticmethod
    def unblock_user(
        session: SessionDep, *, blocker_id: uuid.UUID, blocked_id: uuid.UUID
    ) -> bool:
        """Unblock a user"""
        return user_block.unblock_user(
            session=session, blocker_id=blocker_id, blocked_id=blocked_id
        )

    @staticmethod
    def get_blocked_users(
        session: SessionDep, *, user_id: uuid.UUID
    ) -> List[UserBlock]:
        """Get list of users blocked by the given user"""
        return user_block.get_blocked_users(session=session, blocker_id=user_id)

    @staticmethod
    def is_user_blocked(
        session: SessionDep, *, blocker_id: uuid.UUID, blocked_id: uuid.UUID
    ) -> bool:
        """Check if a user is blocked by another user"""
        return user_block.is_blocked(
            session=session, blocker_id=blocker_id, blocked_id=blocked_id
        )

    @staticmethod
    def record_profile_view(
        session: SessionDep,
        *,
        profile_id: uuid.UUID,
        viewer_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Record a profile view for analytics"""
        profile.record_profile_view(
            session=session,
            profile_id=profile_id,
            viewer_id=viewer_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def get_profile_analytics(session: SessionDep, *, user_id: uuid.UUID) -> dict:
        """Get profile analytics data"""
        user_profile = profile.get_by_user_id(session=session, user_id=user_id)
        if not user_profile:
            return {
                "total_views": 0,
                "unique_viewers": 0,
                "views_last_30_days": 0,
                "close_friends_count": 0,
                "blocked_users_count": 0,
                "profile_completion": 0,
            }

        # Get view statistics
        total_views = profile.get_profile_views_count(
            session=session, profile_id=user_profile.id
        )
        unique_viewers = profile.get_unique_viewers_count(
            session=session, profile_id=user_profile.id
        )

        # Views in last 30 days - for now, just return total (we can add date filtering later)
        recent_views = total_views  # Placeholder

        # Social relationships
        close_friends_count = len(
            close_friend.get_close_friends(session=session, user_id=user_id)
        )
        blocked_count = len(
            user_block.get_blocked_users(session=session, blocker_id=user_id)
        )

        # Profile completion percentage
        completion_fields = [
            user_profile.bio,
            user_profile.website_url,
            user_profile.location,
            user_profile.occupation,
            user_profile.company,
            user_profile.education,
        ]
        completed_fields = sum(1 for field in completion_fields if field)
        profile_completion = int((completed_fields / len(completion_fields)) * 100)

        return {
            "total_views": total_views,
            "unique_viewers": unique_viewers,
            "views_last_30_days": recent_views,
            "close_friends_count": close_friends_count,
            "blocked_users_count": blocked_count,
            "profile_completion": profile_completion,
        }


# Create service instance
profile_service = ProfileService()
