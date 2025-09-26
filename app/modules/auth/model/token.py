import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import JSON, Column, Enum, Field, Relationship, SQLModel

from app.shared.enums import TokenStatus, TokenType

if TYPE_CHECKING:
    from app.modules.auth.model.auth import UserCredentials


class Token(SQLModel, table=True):
    """Token management for authentication"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="usercredentials.id", index=True)

    # Token details
    token: str = Field(max_length=1000, index=True)
    token_type: TokenType
    name: Optional[str] = Field(default=None, max_length=255)  # For API tokens
    status: TokenStatus = Field(default=TokenStatus.ACTIVE)

    # Expiration
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = Field(default=None)
    deactivated_at: Optional[datetime] = Field(default=None)

    # Usage tracking
    usage_count: int = Field(default=0)
    usage_limit: Optional[int] = Field(default=None)

    # Metadata
    user_agent: Optional[str] = Field(default=None, max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    country: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # Relationships
    user_credentials: "UserCredentials" = Relationship(back_populates="tokens")

    class Config:
        orm_mode = True

    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_active(self) -> bool:
        """Check if token is active"""
        return self.status == TokenStatus.ACTIVE and not self.is_expired()

    def can_use(self) -> bool:
        """Check if token can be used"""
        if not self.is_active():
            return False

        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False

        return True

    def increment_usage(self) -> None:
        """Increment usage count"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate token"""
        self.status = TokenStatus.REVOKED
        self.deactivated_at = datetime.utcnow()

    def reactivate(self) -> None:
        """Reactivate token"""
        self.status = TokenStatus.ACTIVE
        self.deactivated_at = None


class TokenBlacklist(SQLModel, table=True):
    """Token blacklist for revoked tokens"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    token: str = Field(max_length=1000, unique=True, index=True)
    token_type: TokenType
    reason: Optional[str] = Field(default=None, max_length=500)
    blacklisted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)

    class Config:
        orm_mode = True

    def is_expired(self) -> bool:
        """Check if blacklist entry is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


class APIToken(SQLModel, table=True):
    """API tokens for programmatic access"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Token details
    name: str = Field(max_length=255)
    token: str = Field(max_length=1000, unique=True, index=True)
    prefix: str = Field(
        max_length=20, index=True
    )  # First few characters for identification
    permissions: List[str] = Field(default=[], sa_column=Column(JSON))

    # Usage tracking
    last_used_at: Optional[datetime] = Field(default=None)
    usage_count: int = Field(default=0)

    # Status
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        orm_mode = True

    def is_expired(self) -> bool:
        """Check if API token is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_active(self) -> bool:
        """Check if API token is active"""
        return self.is_active and not self.is_expired()

    def increment_usage(self) -> None:
        """Increment usage count"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()

    def has_permission(self, permission: str) -> bool:
        """Check if token has specific permission"""
        return permission in self.permissions

    def add_permission(self, permission: str) -> None:
        """Add permission to token"""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: str) -> None:
        """Remove permission from token"""
        if permission in self.permissions:
            self.permissions.remove(permission)
