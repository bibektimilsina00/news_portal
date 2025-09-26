import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.modules.auth.model.token import TokenStatus, TokenType


# Base Token Schemas
class TokenBase(SQLModel):
    """Base token schema"""

    token: str
    token_type: TokenType
    name: Optional[str] = None
    status: TokenStatus = TokenStatus.active
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = None


class TokenCreate(BaseModel):
    """Token creation schema"""

    user_id: uuid.UUID
    token: str
    token_type: TokenType
    name: Optional[str] = None
    expires_at: Optional[datetime] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None


class TokenUpdate(BaseModel):
    """Token update schema"""

    status: Optional[TokenStatus] = None
    last_used_at: Optional[datetime] = None
    usage_count: Optional[int] = None
    is_active: Optional[bool] = None


class TokenResponse(BaseModel):
    """Token response schema"""

    id: uuid.UUID
    token_type: TokenType
    name: Optional[str]
    status: TokenStatus
    expires_at: Optional[datetime]
    created_at: datetime
    last_used_at: Optional[datetime]
    usage_count: int
    usage_limit: Optional[int]
    is_active: bool


class TokenListResponse(BaseModel):
    """Token list response"""

    tokens: List[TokenResponse]
    total: int
    page: int
    per_page: int


# Blacklist Schemas
class TokenBlacklistCreate(BaseModel):
    """Token blacklist creation"""

    token: str
    token_type: TokenType
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None


class TokenBlacklistResponse(BaseModel):
    """Token blacklist response"""

    id: uuid.UUID
    token: str
    token_type: TokenType
    reason: Optional[str]
    blacklisted_at: datetime
    expires_at: Optional[datetime]


# API Token Schemas
class APITokenCreate(BaseModel):
    """API token creation"""

    name: str = Field(..., min_length=1, max_length=255)
    expires_at: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)


class APITokenUpdate(BaseModel):
    """API token update"""

    name: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class APITokenResponse(BaseModel):
    """API token response"""

    id: uuid.UUID
    name: str
    prefix: str
    permissions: List[str]
    is_active: bool
    last_used_at: Optional[datetime]
    usage_count: int
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


# Token Validation Schemas
class TokenValidationRequest(BaseModel):
    """Token validation request"""

    token: str
    token_type: Optional[TokenType] = None


class TokenValidationResponse(BaseModel):
    """Token validation response"""

    valid: bool
    token_type: Optional[TokenType] = None
    expires_at: Optional[datetime] = None
    reason: Optional[str] = None


# Token Statistics Schemas
class TokenStats(BaseModel):
    """Token statistics"""

    total_tokens: int
    active_tokens: int
    expired_tokens: int
    blacklisted_tokens: int
    by_type: Dict[TokenType, int]


# Refresh Token Schemas
class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str
    device_info: Optional[Dict[str, Any]] = None


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: Optional[str] = None


# Revoke Token Schemas
class TokenRevokeRequest(BaseModel):
    """Token revoke request"""

    token: str
    reason: Optional[str] = None


class TokenRevokeResponse(BaseModel):
    """Token revoke response"""

    success: bool
    message: str


# Token Cleanup Schemas
class TokenCleanupResponse(BaseModel):
    """Token cleanup response"""

    cleaned_tokens: int
    affected_users: int
    cleanup_date: datetime


# Security Schemas
class TokenSecurityInfo(BaseModel):
    """Token security information"""

    token_id: uuid.UUID
    token_type: TokenType
    is_active: bool
    is_expired: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    usage_count: int
    usage_limit: Optional[int]
    user_agent: Optional[str]
    ip_address: Optional[str]
    country: Optional[str]
    city: Optional[str]
