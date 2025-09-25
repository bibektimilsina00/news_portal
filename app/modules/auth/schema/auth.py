import enum
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlmodel import SQLModel


# Token Models
class Token(BaseModel):
    """JWT Token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT Token payload"""

    sub: Optional[str] = None  # Subject (user_id)
    exp: Optional[datetime] = None  # Expiration
    type: Optional[str] = None  # Token type (access, refresh, etc.)
    iat: Optional[datetime] = None  # Issued at
    jti: Optional[str] = None  # JWT ID
    scope: Optional[List[str]] = None  # Permissions
    roles: Optional[List[str]] = None  # User roles


# Login Models
class UserLogin(BaseModel):
    """User login request"""

    username_or_email: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    remember_me: bool = Field(default=False)
    device_info: Optional[Dict[str, Any]] = None

    @field_validator("username_or_email")
    @classmethod
    def validate_login_field(cls, v):
        if not v or not v.strip():
            raise ValueError("Username or email is required")
        return v.strip()


class UserLoginResponse(BaseModel):
    """User login response"""

    user_id: uuid.UUID
    username: str
    email: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    is_verified: bool
    account_type: str
    requires_two_factor: bool = False


# Password Reset Models
class PasswordResetRequest(BaseModel):
    """Password reset request"""

    email: EmailStr

    class Config:
        schema_extra = {"example": {"email": "user@example.com"}}


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if info.data and "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        return v


class PasswordResetResponse(BaseModel):
    """Password reset response"""

    message: str = "Password reset successful"
    success: bool = True


# Email Verification Models
class EmailVerificationRequest(BaseModel):
    """Email verification request"""

    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Email verification confirmation"""

    token: str


class EmailVerificationResponse(BaseModel):
    """Email verification response"""

    message: str
    success: bool
    email_verified: bool


# Two-Factor Authentication Models
class TwoFactorSetup(BaseModel):
    """Two-factor authentication setup"""

    secret: str
    qr_code: str
    backup_codes: List[str]


class TwoFactorVerify(BaseModel):
    """Two-factor authentication verification"""

    code: str = Field(..., min_length=6, max_length=6)
    backup_code: Optional[str] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError("Code must be numeric")
        return v


class TwoFactorResponse(BaseModel):
    """Two-factor authentication response"""

    enabled: bool
    backup_codes: Optional[List[str]] = None


# API Token Models
class APITokenCreate(BaseModel):
    """API token creation request"""

    name: str = Field(..., min_length=1, max_length=255)
    expires_in_days: Optional[int] = Field(default=30, ge=1, le=365)
    permissions: Optional[List[str]] = Field(default=[])

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Token name cannot be empty")
        return v.strip()


class APITokenResponse(BaseModel):
    """API token response"""

    id: uuid.UUID
    name: str
    token: str  # Only shown once!
    prefix: str
    permissions: List[str]
    expires_at: Optional[datetime]
    created_at: datetime


class APITokenList(BaseModel):
    """API token list response"""

    tokens: List[APITokenResponse]
    total: int


# Device Management Models
class DeviceInfo(BaseModel):
    """Device information for login tracking"""

    device_type: Optional[str] = None  # mobile, desktop, tablet
    device_name: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None
    app_version: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None


class LoginDevice(BaseModel):
    """Login device information"""

    id: uuid.UUID
    device_info: DeviceInfo
    login_at: datetime
    last_active_at: datetime
    is_current_device: bool = False


class DeviceList(BaseModel):
    """Device list response"""

    devices: List[LoginDevice]
    total: int


# Security Models
class SecuritySettings(BaseModel):
    """User security settings"""

    two_factor_enabled: bool = False
    login_notifications: bool = True
    new_device_alerts: bool = True
    password_expires_days: Optional[int] = None
    max_failed_attempts: int = Field(default=5, ge=3, le=10)
    account_lockout_duration: int = Field(default=30, ge=15, le=1440)  # minutes


class SecurityLog(BaseModel):
    """Security log entry"""

    id: uuid.UUID
    event_type: str
    event_status: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    country: Optional[str]
    city: Optional[str]
    details: Optional[str]
    error_message: Optional[str]
    created_at: datetime


class SecurityLogsResponse(BaseModel):
    """Security logs response"""

    logs: List[SecurityLog]
    total: int
    page: int
    per_page: int


# Rate Limiting Models
class RateLimitStatus(BaseModel):
    """Rate limit status"""

    limit: int
    remaining: int
    reset_at: datetime
    retry_after: Optional[int] = None


# OAuth2 Models
class OAuth2Provider(str, enum.Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    GITHUB = "github"
    MICROSOFT = "microsoft"


class OAuth2Login(BaseModel):
    """OAuth2 login request"""

    provider: OAuth2Provider
    access_token: str
    refresh_token: Optional[str] = None


class OAuth2Callback(BaseModel):
    """OAuth2 callback data"""

    code: str
    state: Optional[str] = None


# Session Models
class SessionInfo(BaseModel):
    """Session information"""

    id: uuid.UUID
    user_agent: Optional[str]
    ip_address: Optional[str]
    country: Optional[str]
    city: Optional[str]
    login_at: datetime
    last_active_at: datetime
    expires_at: datetime
    is_current_session: bool = False


class SessionList(BaseModel):
    """Session list response"""

    sessions: List[SessionInfo]
    total: int


# Response Models
class AuthResponse(BaseModel):
    """Base authentication response"""

    success: bool
    message: str


class LoginResponse(AuthResponse):
    """Login response"""

    data: Optional[UserLoginResponse] = None


class LogoutResponse(AuthResponse):
    """Logout response"""

    message: str = "Logged out successfully"


# Token Refresh Models
class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str = Field(..., min_length=1)

    @field_validator("refresh_token")
    @classmethod
    def validate_refresh_token(cls, v):
        if not v or not v.strip():
            raise ValueError("Refresh token is required")
        return v.strip()


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


# Token Revoke Models
class TokenRevokeRequest(BaseModel):
    """Token revoke request"""

    token: str = Field(..., min_length=1)

    @field_validator("token")
    @classmethod
    def validate_token(cls, v):
        if not v or not v.strip():
            raise ValueError("Token is required")
        return v.strip()


class TokenRevokeResponse(BaseModel):
    """Token revoke response"""

    success: bool
    message: str = "Token revoked successfully"


# Error Models
class AuthError(BaseModel):
    """Authentication error"""

    error: str
    error_description: Optional[str] = None
    error_code: Optional[str] = None


# Config Models
class AuthConfig(BaseModel):
    """Authentication configuration"""

    access_token_expire_minutes: int
    refresh_token_expire_days: int
    password_reset_expire_minutes: int
    email_verification_expire_hours: int
    max_failed_attempts: int
    account_lockout_duration_minutes: int
    two_factor_enabled: bool
    oauth_providers: List[str]
