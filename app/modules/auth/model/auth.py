import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.auth.model.token import Token
    from app.modules.users.model.user import User


class UserCredentials(SQLModel, table=True):
    """User credentials for authentication"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)

    # Authentication fields
    password_hash: str = Field(max_length=255)
    password_changed_at: Optional[datetime] = Field(default=None)

    # Security fields
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)
    last_login_at: Optional[datetime] = Field(default=None)
    last_login_ip: Optional[str] = Field(default=None, max_length=45)

    # Two-factor authentication
    two_factor_enabled: bool = Field(default=False)
    two_factor_secret: Optional[str] = Field(default=None, max_length=255)
    backup_codes: Optional[str] = Field(
        default=None, max_length=2000
    )  # JSON string of backup codes

    # Account security
    email_verified: bool = Field(default=False)
    email_verified_at: Optional[datetime] = Field(default=None)
    phone_verified: bool = Field(default=False)
    phone_verified_at: Optional[datetime] = Field(default=None)

    # Status
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Relationships
    user: "User" = Relationship(back_populates="credentials")
    tokens: List["Token"] = Relationship(back_populates="user")

    model_config = {"from_attributes": True}

    def is_locked(self) -> bool:
        """Check if account is locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def increment_failed_attempts(self) -> int:
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        return self.failed_login_attempts

    def reset_failed_attempts(self) -> None:
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None

    def lock_account(self, duration_minutes: int = 30) -> None:
        """Lock account for specified duration"""
        from datetime import timedelta

        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)


class PasswordResetToken(SQLModel, table=True):
    """Password reset tokens"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    token: str = Field(max_length=500, index=True)
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    used_at: Optional[datetime] = Field(default=None)

    class Config:
        from_attributes = True

    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at

    def mark_as_used(self) -> None:
        """Mark token as used"""
        self.used = True
        self.used_at = datetime.utcnow()


class EmailVerificationToken(SQLModel, table=True):
    """Email verification tokens"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    email: str = Field(max_length=255, index=True)
    token: str = Field(max_length=500, index=True)
    used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    used_at: Optional[datetime] = Field(default=None)

    class Config:
        from_attributes = True

    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at

    def mark_as_used(self) -> None:
        """Mark token as used"""
        self.used = True
        self.used_at = datetime.utcnow()


class SecurityLog(SQLModel, table=True):
    """Security logs for tracking authentication events"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", index=True
    )

    # Event details
    event_type: str = Field(
        max_length=50
    )  # login, logout, failed_login, password_reset, etc.
    event_status: str = Field(max_length=20)  # success, failed, blocked
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # Additional context
    details: Optional[str] = Field(default=None, max_length=1000)
    error_message: Optional[str] = Field(default=None, max_length=500)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
