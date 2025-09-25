import uuid
from typing import List, Optional

from sqlmodel import Session, select

from app.modules.users.model.profile import CloseFriend, Profile, ProfileView, UserBlock
from app.modules.users.schema.profile import ProfileCreate, ProfileUpdate
from app.shared.crud.base import CRUDBase


class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    """CRUD operations for Profile model"""

    def get_by_user_id(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[Profile]:
        """Get profile by user ID"""
        statement = select(Profile).where(Profile.user_id == user_id)
        return session.exec(statement).first()

    def create_profile_for_user(
        self, session: Session, *, user_id: uuid.UUID, profile_data: dict
    ) -> Profile:
        """Create a new profile for a user"""
        profile_data["user_id"] = user_id
        db_obj = Profile(**profile_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update_profile(
        self, session: Session, *, profile: Profile, update_data: dict
    ) -> Profile:
        """Update profile information"""
        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        # Update timestamp manually
        from datetime import datetime

        profile.updated_at = datetime.utcnow()
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile

    def record_profile_view(
        self,
        session: Session,
        *,
        profile_id: uuid.UUID,
        viewer_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ProfileView:
        """Record a profile view"""
        view = ProfileView(
            profile_id=profile_id,
            viewer_id=viewer_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(view)
        session.commit()
        session.refresh(view)
        return view

    def get_profile_views_count(
        self, session: Session, *, profile_id: uuid.UUID
    ) -> int:
        """Get total profile views count"""
        statement = select(ProfileView).where(ProfileView.profile_id == profile_id)
        return len(session.exec(statement).all())

    def get_unique_viewers_count(
        self, session: Session, *, profile_id: uuid.UUID
    ) -> int:
        """Get unique viewers count"""
        statement = (
            select(ProfileView.viewer_id)
            .where(
                ProfileView.profile_id == profile_id, ProfileView.viewer_id.isnot(None)
            )
            .distinct()
        )
        return len(session.exec(statement).all())


class CRUDCloseFriend:
    """CRUD operations for CloseFriend model"""

    def add_close_friend(
        self, session: Session, *, user_id: uuid.UUID, friend_id: uuid.UUID
    ) -> CloseFriend:
        """Add a user to close friends"""
        # Check if relationship already exists
        existing = session.exec(
            select(CloseFriend).where(
                CloseFriend.user_id == user_id, CloseFriend.friend_id == friend_id
            )
        ).first()

        if existing:
            return existing

        friend = CloseFriend(user_id=user_id, friend_id=friend_id)
        session.add(friend)
        session.commit()
        session.refresh(friend)
        return friend

    def remove_close_friend(
        self, session: Session, *, user_id: uuid.UUID, friend_id: uuid.UUID
    ) -> bool:
        """Remove a user from close friends"""
        friend = session.exec(
            select(CloseFriend).where(
                CloseFriend.user_id == user_id, CloseFriend.friend_id == friend_id
            )
        ).first()

        if friend:
            session.delete(friend)
            session.commit()
            return True
        return False

    def get_close_friends(
        self, session: Session, *, user_id: uuid.UUID
    ) -> List[CloseFriend]:
        """Get all close friends for a user"""
        statement = select(CloseFriend).where(CloseFriend.user_id == user_id)
        return list(session.exec(statement))

    def is_close_friend(
        self, session: Session, *, user_id: uuid.UUID, friend_id: uuid.UUID
    ) -> bool:
        """Check if a user is in close friends"""
        friend = session.exec(
            select(CloseFriend).where(
                CloseFriend.user_id == user_id, CloseFriend.friend_id == friend_id
            )
        ).first()
        return friend is not None


class CRUDUserBlock:
    """CRUD operations for UserBlock model"""

    def block_user(
        self,
        session: Session,
        *,
        blocker_id: uuid.UUID,
        blocked_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> UserBlock:
        """Block a user"""
        # Check if block already exists
        existing = session.exec(
            select(UserBlock).where(
                UserBlock.blocker_id == blocker_id, UserBlock.blocked_id == blocked_id
            )
        ).first()

        if existing:
            return existing

        block = UserBlock(blocker_id=blocker_id, blocked_id=blocked_id, reason=reason)
        session.add(block)
        session.commit()
        session.refresh(block)
        return block

    def unblock_user(
        self, session: Session, *, blocker_id: uuid.UUID, blocked_id: uuid.UUID
    ) -> bool:
        """Unblock a user"""
        block = session.exec(
            select(UserBlock).where(
                UserBlock.blocker_id == blocker_id, UserBlock.blocked_id == blocked_id
            )
        ).first()

        if block:
            session.delete(block)
            session.commit()
            return True
        return False

    def get_blocked_users(
        self, session: Session, *, blocker_id: uuid.UUID
    ) -> List[UserBlock]:
        """Get all users blocked by a user"""
        statement = select(UserBlock).where(UserBlock.blocker_id == blocker_id)
        return list(session.exec(statement))

    def is_blocked(
        self, session: Session, *, blocker_id: uuid.UUID, blocked_id: uuid.UUID
    ) -> bool:
        """Check if a user is blocked"""
        block = session.exec(
            select(UserBlock).where(
                UserBlock.blocker_id == blocker_id, UserBlock.blocked_id == blocked_id
            )
        ).first()
        return block is not None

    def is_blocking_me(
        self, session: Session, *, user_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> bool:
        """Check if another user has blocked me"""
        return self.is_blocked(
            session=session, blocker_id=other_user_id, blocked_id=user_id
        )


# Create singleton instances
profile = CRUDProfile(Profile)
close_friend = CRUDCloseFriend()
user_block = CRUDUserBlock()
