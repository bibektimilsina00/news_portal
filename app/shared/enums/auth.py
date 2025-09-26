import enum


class OAuth2Provider(str, enum.Enum):
    google = "google"
    facebook = "facebook"
    twitter = "twitter"
    github = "github"
    microsoft = "microsoft"


class TokenType(str, enum.Enum):
    access = "access"
    refresh = "refresh"
    password_reset = "password_reset"
    email_verification = "email_verification"
    api = "api"


class TokenStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    revoked = "revoked"
    blacklisted = "blacklisted"
