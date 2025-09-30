import uuid
from typing import Any, Dict, List, Optional

from sqlmodel import Session, func, select

from app.modules.social.model.follow import Follow
from app.modules.users.crud.crud_user import crud_user
from app.modules.users.model.user import AccountType, User
from app.modules.users.schema.user import UserCreate, UserUpdate
from app.shared.exceptions.exceptions import (
    InvalidUserDataException,
    UnauthorizedException,
    UserAlreadyExistsException,
    UserNotFoundException,
)


class UserService:
    """Service layer for crud_user management with Instagram-style news platform features"""

    @staticmethod
    def create_user(*, session: Session, user_create: UserCreate) -> User:
        """Create new crud_user with validation"""
        # Check if email already exists
        existing_user = crud_user.get_by_email(session=session, email=user_create.email)
        if existing_user:
            raise UserAlreadyExistsException("Email already registered")

        # Check if username already exists
        existing_user = crud_user.get_by_username(
            session=session, username=user_create.username
        )
        if existing_user:
            raise UserAlreadyExistsException("Username already taken")

        return crud_user.create(session=session, obj_in=user_create)

    @staticmethod
    def get_user(session: Session, user_id: uuid.UUID) -> Optional[User]:
        """Get crud_user by ID"""
        db_user = crud_user.get(session=session, id=user_id)
        if not db_user:
            raise UserNotFoundException("User not found")
        return db_user

    @staticmethod
    def get_user_by_email(*, session: Session, email: str) -> Optional[User]:
        """Get crud_user by email"""
        return crud_user.get_by_email(session=session, email=email)

    @staticmethod
    def get_user_by_username(*, session: Session, username: str) -> Optional[User]:
        """Get crud_user by username"""
        return crud_user.get_by_username(session=session, username=username)

    @staticmethod
    def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> Optional[User]:
        """Get crud_user by UUID"""
        return crud_user.get_by_id(session=session, user_id=user_id)

    @staticmethod
    def get_users(session: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users with pagination"""
        return crud_user.get_multi(session=session, skip=skip, limit=limit)

    @staticmethod
    def get_verified_users(
        session: Session, *, skip: int = 0, limit: int = 50
    ) -> List[User]:
        """Get all verified users (journalists, news organizations, etc.)"""
        return crud_user.get_verified_users(session=session, skip=skip, limit=limit)

    @staticmethod
    def get_journalists(
        session: Session, *, skip: int = 0, limit: int = 50
    ) -> List[User]:
        """Get all journalist users"""
        return crud_user.get_journalists(session=session, skip=skip, limit=limit)

    @staticmethod
    def get_by_account_type(
        session: Session, *, account_type: AccountType, skip: int = 0, limit: int = 50
    ) -> List[User]:
        """Get users by account type"""
        return crud_user.get_by_account_type(
            session=session, account_type=account_type, skip=skip, limit=limit
        )

    @staticmethod
    def update_user(
        *, session: Session, db_user: User, user_in: UserUpdate | Dict[str, Any]
    ) -> User:
        """Update user information"""
        return crud_user.update(session=session, db_obj=db_user, obj_in=user_in)

    @staticmethod
    def update_last_active(*, session: Session, user_id: uuid.UUID) -> Optional[User]:
        """Update user's last active timestamp"""
        return crud_user.update_last_active(session=session, user_id=user_id)

    @staticmethod
    def delete_user(*, session: Session, user_id: uuid.UUID) -> bool:
        """Delete crud_user and cascade delete related data"""
        db_user = crud_user.get(session=session, id=user_id)
        if not db_user:
            raise UserNotFoundException("User not found")

        # Prevent deleting superusers
        if db_user.is_superuser:
            raise UnauthorizedException("Cannot delete superuser")

        # Delete crud_user (cascade will handle relationships)
        session.delete(db_user)
        session.commit()
        return True

    @staticmethod
    def authenticate_user(
        *, session: Session, login: str, password: str
    ) -> Optional[User]:
        """
        Authenticate crud_user with email OR username and password.
        Updates last active timestamp on successful authentication.
        """
        db_user = crud_user.authenticate(
            session=session, email=login, password=password
        )
        if not db_user:
            raise InvalidUserDataException("Invalid credentials")

        if not db_user.is_active:
            raise UnauthorizedException("User account is not active")

        return db_user

    @staticmethod
    def search_users(
        *, session: Session, query: str, skip: int = 0, limit: int = 20
    ) -> List[User]:
        """Search users by username, full_name, or email"""
        return crud_user.search_users(
            session=session, query=query, skip=skip, limit=limit
        )

    @staticmethod
    def is_active(crud_user: User) -> bool:
        """Check if crud_user is active"""
        return crud_user.is_active

    @staticmethod
    def is_verified(crud_user: User) -> bool:
        """Check if crud_user is verified"""
        return crud_user.is_verified

    @staticmethod
    def is_superuser(crud_user: User) -> bool:
        """Check if crud_user is superuser"""
        return crud_user.is_superuser

    @staticmethod
    def is_journalist(crud_user: User) -> bool:
        """Check if crud_user is a journalist"""
        return crud_user.is_journalist

    @staticmethod
    def is_organization(crud_user: User) -> bool:
        """Check if crud_user is an organization"""
        return crud_user.is_organization

    @staticmethod
    def can_post_verified_content(crud_user: User) -> bool:
        """Check if crud_user can post verified news content"""
        return crud_user.can_post_verified_content(crud_user)

    @staticmethod
    def is_following(
        *, session: Session, follower_id: uuid.UUID, following_id: uuid.UUID
    ) -> bool:
        """Check if one crud_user follows another"""
        statement = select(Follow).where(
            and_(Follow.follower_id == follower_id, Follow.following_id == following_id)
        )
        return session.exec(statement).first() is not None

    @staticmethod
    def get_mutual_followers_count(
        *, session: Session, user_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> int:
        """Get count of mutual followers between two users"""
        # Get followers of crud_user
        user_followers = select(Follow.follower_id).where(
            Follow.following_id == user_id
        )

        # Get followers of other crud_user
        other_followers = select(Follow.follower_id).where(
            Follow.following_id == other_user_id
        )

        # Count intersection
        mutual = select(func.count()).select_from(
            user_followers.intersect(other_followers)
        )
        return session.exec(mutual).one()

    @staticmethod
    def get_user_stats(*, session: Session, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive crud_user statistics"""
        return crud_user.get_user_stats(session=session, user_id=user_id)

    @staticmethod
    def count_users(session: Session) -> int:
        """Get total crud_user count"""
        return crud_user.count(session=session)

    @staticmethod
    def count_verified_users(session: Session) -> int:
        """Get verified crud_user count"""
        statement = select(func.count(User.id)).where(User.is_verified == True)
        return session.exec(statement).one()

    @staticmethod
    def count_journalists(session: Session) -> int:
        """Get journalist crud_user count"""
        statement = select(func.count(User.id)).where(User.is_journalist == True)
        return session.exec(statement).one()

    @staticmethod
    def get_user_by_verification_token(
        *, session: Session, token: str
    ) -> Optional[User]:
        """Get crud_user by verification token (for email verification)"""
        # This would depend on your verification token implementation
        # For now, return None - implement based on your token system
        return None

    @staticmethod
    def verify_user(*, session: Session, user_id: uuid.UUID) -> Optional[User]:
        """Mark crud_user as verified"""
        db_user = crud_user.get(session=session, id=user_id)
        if not db_user:
            raise UserNotFoundException("User not found")

        if db_user.is_verified:
            return db_user  # Already verified

        return crud_user.update(
            session=session, db_obj=db_user, obj_in={"is_verified": True}
        )

    @staticmethod
    def deactivate_user(*, session: Session, user_id: uuid.UUID) -> Optional[User]:
        """Deactivate crud_user account"""
        db_user = crud_user.get(session=session, id=user_id)
        if not db_user:
            raise UserNotFoundException("User not found")

        return crud_user.update(
            session=session, db_obj=db_user, obj_in={"is_active": False}
        )

    @staticmethod
    def reactivate_user(*, session: Session, user_id: uuid.UUID) -> Optional[User]:
        """Reactivate crud_user account"""
        db_user = crud_user.get(session=session, id=user_id)
        if not db_user:
            raise UserNotFoundException("User not found")

        return crud_user.update(
            session=session, db_obj=db_user, obj_in={"is_active": True}
        )

    @staticmethod
    def get_active_users_count(session: Session) -> int:
        """Get count of active users"""
        statement = select(func.count(User.id)).where(User.is_active)
        return session.exec(statement).one()

    @staticmethod
    def get_inactive_users_count(session: Session) -> int:
        """Get count of inactive users"""
        statement = select(func.count(User.id)).where(User.is_active)
        return session.exec(statement).one()


# Create singleton instance
user_service = UserService()
