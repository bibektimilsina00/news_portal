import uuid
from typing import Any, List, Optional

from sqlalchemy import and_
from sqlmodel import Session, func, or_, select

from app.core.security import get_password_hash, verify_password
from app.modules.users.model.user import User
from app.modules.users.schema.user import AccountType, Gender, UserCreate, UserUpdate
from app.shared.crud.base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model with Instagram-style news platform features"""

    def get_by_email(self, session: Session, *, email: str) -> Optional[User]:
        """Get user by email address"""
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()

    def get_by_username(self, session: Session, *, username: str) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(User.username == username)
        return session.exec(statement).first()

    def get_by_id(self, session: Session, *, user_id: uuid.UUID) -> Optional[User]:
        """Get user by UUID"""
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).first()

    def get_by_email_or_username(
        self, session: Session, *, login: str
    ) -> Optional[User]:
        """Get user by email OR username (for login)"""
        statement = select(User).where(or_(User.email == login, User.username == login))
        return session.exec(statement).first()

    def create(self, session: Session, *, obj_in: UserCreate) -> User:
        """Create new user with Instagram-style news platform features"""
        create_data = obj_in.model_dump()
        create_data.pop("password", None)

        # Set username to lowercase for consistency
        if "username" in create_data:
            create_data["username"] = create_data["username"].lower()

        # Hash the password
        db_obj = User(**create_data)
        db_obj.hashed_password = get_password_hash(obj_in.password)
        db_obj.created_at = func.now()

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self, session: Session, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        """Update user information"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Handle password update
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        # Set username to lowercase if provided
        if "username" in update_data:
            update_data["username"] = update_data["username"].lower()

        # Update timestamp
        update_data["updated_at"] = func.now()

        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update_last_active(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[User]:
        """Update user's last active timestamp"""
        user = self.get_by_id(session=session, user_id=user_id)
        if user:
            user.last_active = func.now()
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def update_social_counts(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[User]:
        """Update user's social media counters"""
        user = self.get_by_id(session=session, user_id=user_id)
        if user:
            # These would normally come from database queries
            # For now, just update the timestamp
            user.updated_at = func.now()
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def increment_follower_count(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[User]:
        """Increment follower count"""
        user = self.get_by_id(session=session, user_id=user_id)
        if user:
            user.follower_count += 1
            user.updated_at = func.now()
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def decrement_follower_count(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[User]:
        """Decrement follower count"""
        user = self.get_by_id(session=session, user_id=user_id)
        if user and user.follower_count > 0:
            user.follower_count -= 1
            user.updated_at = func.now()
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def increment_following_count(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[User]:
        """Increment following count"""
        user = self.get_by_id(session=session, user_id=user_id)
        if user:
            user.following_count += 1
            user.updated_at = func.now()
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def decrement_following_count(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[User]:
        """Decrement following count"""
        user = self.get_by_id(session=session, user_id=user_id)
        if user and user.following_count > 0:
            user.following_count -= 1
            user.updated_at = func.now()
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def increment_post_count(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[User]:
        """Increment post count"""
        user = self.get_by_id(session=session, user_id=user_id)
        if user:
            user.post_count += 1
            user.updated_at = func.now()
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def decrement_post_count(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Optional[User]:
        """Decrement post count"""
        user = self.get_by_id(session=session, user_id=user_id)
        if user and user.post_count > 0:
            user.post_count -= 1
            user.updated_at = func.now()
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def authenticate(
        self, session: Session, *, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user with email/username and password"""
        # Try to find user by email or username
        user = self.get_by_email_or_username(session=session, login=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        # Update last active on successful login
        self.update_last_active(session=session, user_id=user.id)
        return user

    def search_users(
        self, session: Session, *, query: str, skip: int = 0, limit: int = 20
    ) -> List[User]:
        """Search users by username, full_name, or email"""
        statement = (
            select(User)
            .where(
                and_(
                    User.is_active == True,
                    or_(
                        User.username.ilike(f"%{query}%"),
                        User.full_name.ilike(f"%{query}%"),
                        User.email.ilike(f"%{query}%"),
                    ),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_verified_users(
        self, session: Session, skip: int = 0, limit: int = 50
    ) -> List[User]:
        """Get all verified users"""
        statement = (
            select(User)
            .where(and_(User.is_verified == True, User.is_active == True))
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_journalists(
        self, session: Session, skip: int = 0, limit: int = 50
    ) -> List[User]:
        """Get all journalist users"""
        statement = (
            select(User)
            .where(and_(User.is_journalist == True, User.is_active == True))
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_by_account_type(
        self,
        session: Session,
        account_type: AccountType,
        skip: int = 0,
        limit: int = 50,
    ) -> List[User]:
        """Get users by account type"""
        statement = (
            select(User)
            .where(and_(User.account_type == account_type, User.is_active == True))
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active

    def is_verified(self, user: User) -> bool:
        """Check if user is verified"""
        return user.is_verified

    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser"""
        return user.is_superuser

    def is_journalist(self, user: User) -> bool:
        """Check if user is a journalist"""
        return user.is_journalist

    def is_organization(self, user: User) -> bool:
        """Check if user is an organization"""
        return user.is_organization

    def can_post_verified_content(self, user: User) -> bool:
        """Check if user can post verified content"""
        return user.is_verified or user.is_journalist or user.is_organization

    def get_user_stats(self, session: Session, *, user_id: uuid.UUID) -> dict:
        """Get comprehensive user statistics"""
        user = self.get_by_id(session=session, user_id=user_id)
        if not user:
            return {}

        return {
            "user_id": user.id,
            "follower_count": user.follower_count,
            "following_count": user.following_count,
            "post_count": user.post_count,
            "account_type": user.account_type,
            "is_verified": user.is_verified,
            "is_journalist": user.is_journalist,
            "last_active": user.last_active,
            "created_at": user.created_at,
        }


# Create singleton instance
user = CRUDUser(User)
