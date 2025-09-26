"""
OAuth service for handling OAuth authentication logic
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.auth.crud.crud_auth import CRUDAuth
from app.modules.auth.schema.auth import OAuth2Provider, UserLoginResponse
from app.modules.users.model.user import User
from app.shared.enums.account_type import AccountType


class OAuthService:
    """Service for OAuth operations"""

    def __init__(self):
        self.auth_crud = CRUDAuth()

    async def process_oauth_login(
        self,
        session: Session,
        provider: OAuth2Provider,
        user_info: Dict[str, Any],
        oauth_token: Dict[str, Any],
    ) -> UserLoginResponse:
        """Process OAuth login and return user login response"""

        # Extract user information from OAuth provider
        email = user_info.get("email")
        if not email:
            raise ValueError("Email not provided by OAuth provider")

        # Try to find existing user by email
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            # Create new user from OAuth data
            user = self._create_user_from_oauth(session, provider, user_info)

        # Update user's last active time
        user.last_active = datetime.utcnow()
        session.add(user)
        session.commit()
        session.refresh(user)

        # Generate tokens
        access_token = self.auth_crud.create_access_token(str(user.id))
        refresh_token = self.auth_crud.create_refresh_token(str(user.id))

        # Calculate token expiration
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        return UserLoginResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            is_verified=user.is_verified,
            account_type=user.account_type.value,
            requires_two_factor=False,  # OAuth doesn't use 2FA for now
        )

    async def validate_oauth_token(
        self, provider: OAuth2Provider, access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Validate OAuth access token with provider"""

        try:
            if provider == OAuth2Provider.GOOGLE:
                return await self._validate_google_token(access_token)
            elif provider == OAuth2Provider.FACEBOOK:
                return await self._validate_facebook_token(access_token)
            elif provider == OAuth2Provider.GITHUB:
                return await self._validate_github_token(access_token)
            elif provider == OAuth2Provider.TWITTER:
                return await self._validate_twitter_token(access_token)
            else:
                return None
        except Exception:
            return None

    async def unlink_oauth_provider(
        self, session: Session, user_id: uuid.UUID, provider: OAuth2Provider
    ) -> bool:
        """Unlink OAuth provider from user account"""
        # For now, just return True since OAuth provider linking is not implemented yet
        # In the future, this would remove OAuth provider association from user
        return True

    def _create_user_from_oauth(
        self, session: Session, provider: OAuth2Provider, user_info: Dict[str, Any]
    ) -> User:
        """Create new user from OAuth provider data"""

        email = user_info.get("email")
        if not email or not isinstance(email, str):
            raise ValueError("Valid email not provided by OAuth provider")

        name = (
            user_info.get("name")
            or user_info.get("login")
            or user_info.get("screen_name")
        )

        # Generate unique username
        base_username = self._generate_username_from_email(email)
        username = self._ensure_unique_username(session, base_username)

        # Create user
        user = User(
            username=username,
            email=email,
            full_name=name,
            hashed_password=self._generate_random_password(),
            is_active=True,
            is_verified=True,  # OAuth users are pre-verified
            account_type=AccountType.PERSONAL,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def _generate_username_from_email(self, email: str) -> str:
        """Generate username from email"""
        username = email.split("@")[0]
        # Remove non-alphanumeric characters
        username = "".join(c for c in username if c.isalnum() or c in "_-")
        return username.lower()

    def _ensure_unique_username(self, session: Session, base_username: str) -> str:
        """Ensure username is unique by appending numbers if needed"""
        username = base_username
        counter = 1

        while session.exec(select(User).where(User.username == username)).first():
            username = f"{base_username}{counter}"
            counter += 1

        return username

    def _generate_random_password(self) -> str:
        """Generate a random password for OAuth users"""
        return secrets.token_urlsafe(32)

    async def _validate_google_token(
        self, access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Validate Google OAuth token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 200:
                return response.json()
        return None

    async def _validate_facebook_token(
        self, access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Validate Facebook OAuth token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.facebook.com/me",
                params={"fields": "id,name,email", "access_token": access_token},
            )
            if response.status_code == 200:
                return response.json()
        return None

    async def _validate_github_token(
        self, access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Validate GitHub OAuth token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 200:
                return response.json()
        return None

    async def _validate_twitter_token(
        self, access_token: str
    ) -> Optional[Dict[str, Any]]:
        """Validate Twitter OAuth token"""
        # Twitter OAuth 2.0 validation would require different implementation
        # For now, return None as Twitter OAuth might not be fully implemented
        return None


# Create service instance
oauth_service = OAuthService()
