from enum import Enum


class TokenType(str, Enum):
    """Token types for authentication"""

    access = "access"
    refresh = "refresh"
    api = "api"


class TokenStatus(str, Enum):
    """Token status values"""

    active = "active"
    expired = "expired"
    revoked = "revoked"
    suspended = "suspended"
