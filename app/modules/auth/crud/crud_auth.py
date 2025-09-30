import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.modules.auth.model.auth import UserCredentials
from app.modules.auth.schema.token import TokenCreate, TokenUpdate
from app.shared.crud.base import CRUDBase


class CRUDAuth(CRUDBase[UserCredentials, TokenCreate, TokenUpdate]):
    """CRUD operations for authentication with JWT tokens"""

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return self.pwd_context.hash(password)

    def create_access_token(
        self,
        subject: str | Any,
        expires_delta: timedelta | None = None,
        additional_claims: Dict[str, Any] | None = None,
    ) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {"exp": expire, "sub": str(subject), "type": "access"}

        if additional_claims:
            to_encode.update(additional_claims)

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(
        self, subject: str | Any, expires_delta: timedelta | None = None
    ) -> str:
        """Create JWT refresh token"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh",
            "iat": datetime.now(timezone.utc).timestamp(),
        }

        encoded_jwt = jwt.encode(
            to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Optional[str]:
        """Verify JWT token and return subject"""
        try:
            if token_type == "refresh":
                secret_key = settings.REFRESH_SECRET_KEY
            else:
                secret_key = settings.SECRET_KEY

            payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])

            if payload.get("type") != token_type:
                return None

            return payload.get("sub")
        except JWTError:
            return None

    def decode_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """Decode JWT token and return full payload"""
        try:
            if token_type == "refresh":
                secret_key = settings.REFRESH_SECRET_KEY
            else:
                secret_key = settings.SECRET_KEY

            payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])

            if payload.get("type") != token_type:
                return None

            return payload
        except JWTError:
            return None

    def create_password_reset_token(self, email: str) -> str:
        """Create password reset token"""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
        )

        to_encode = {
            "exp": expire,
            "sub": email,
            "type": "password_reset",
            "iat": datetime.now(timezone.utc).timestamp(),
        }

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return email"""
        payload = self.decode_token(token, "password_reset")
        if payload and payload.get("type") == "password_reset":
            return payload.get("sub")
        return None

    def create_email_verification_token(self, email: str) -> str:
        """Create email verification token"""
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
        )

        to_encode = {
            "exp": expire,
            "sub": email,
            "type": "email_verification",
            "iat": datetime.now(timezone.utc).timestamp(),
        }

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def verify_email_verification_token(self, token: str) -> Optional[str]:
        """Verify email verification token and return email"""
        payload = self.decode_token(token, "email_verification")
        if payload and payload.get("type") == "email_verification":
            return payload.get("sub")
        return None

    def create_api_token(
        self, user_id: uuid.UUID, name: str, expires_delta: timedelta | None = None
    ) -> str:
        """Create long-lived API token"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.API_TOKEN_EXPIRE_DAYS
            )

        to_encode = {
            "exp": expire,
            "sub": str(user_id),
            "type": "api",
            "name": name,
            "iat": datetime.now(timezone.utc).timestamp(),
        }

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def blacklist_token(
        self, session: Session, token: str, token_type: str = "access"
    ) -> bool:
        """Blacklist a token (logout functionality)"""
        # This would typically store in Redis or database
        # For now, we'll just validate it exists
        payload = self.decode_token(token, token_type)
        return payload is not None


# Create singleton instance
auth = CRUDAuth()
