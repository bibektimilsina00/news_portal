"""
Authentication service for handling user authentication logic
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlmodel import Session, desc, or_, select

from app.core.config import settings
from app.modules.auth.crud.crud_auth import CRUDAuth
from app.modules.auth.crud.crud_token import CRUDToken
from app.modules.auth.model.auth import SecurityLog, UserCredentials
from app.modules.auth.model.token import Token, TokenStatus, TokenType
from app.modules.auth.schema.auth import (
    DeviceInfo,
    DeviceList,
    LoginDevice,
    SecurityLogsResponse,
    SecuritySettings,
)
from app.modules.users.model.user import User


class AuthService:
    """Service for authentication operations"""

    def __init__(self):
        self.auth_crud = CRUDAuth()
        self.token_crud = CRUDToken(Token)

    async def authenticate_user(
        self, session: Session, login: str, password: str
    ) -> Optional[User]:
        """Authenticate user with username/email and password"""
        # Find user by username or email
        user = (
            session.query(User)
            .filter(or_(User.username == login, User.email == login))
            .first()
        )

        if not user:
            return None

        # Verify password against user's hashed_password
        if not self.auth_crud.verify_password(password, user.hashed_password):
            return None

        return user

    async def create_user_session(
        self,
        session: Session,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Token:
        """Create a new user session with access and refresh tokens"""
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.auth_crud.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )

        # Create refresh token
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token = self.auth_crud.create_refresh_token(
            subject=str(user.id), expires_delta=refresh_token_expires
        )

        # Store tokens in database
        access_token_obj = self.token_crud.create_token(
            session=session,
            user_id=user.id,
            token=access_token,
            token_type=TokenType.access,
            expires_at=datetime.utcnow() + access_token_expires,
        )

        refresh_token_obj = self.token_crud.create_token(
            session=session,
            user_id=user.id,
            token=refresh_token,
            token_type=TokenType.refresh,
            expires_at=datetime.utcnow() + refresh_token_expires,
        )

        return access_token_obj

    def refresh_access_token(
        self, session: Session, refresh_token: str
    ) -> Optional[Token]:
        """Refresh access token using refresh token"""
        # Verify refresh token
        user_id_str = self.auth_crud.verify_token(refresh_token, "refresh")
        if not user_id_str:
            return None

        user_id = UUID(user_id_str)

        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.auth_crud.create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )

        # Store new access token
        token_obj = self.token_crud.create_token(
            session=session,
            user_id=user_id,
            token=access_token,
            token_type=TokenType.access,
            expires_at=datetime.utcnow() + access_token_expires,
        )

        return token_obj

    def logout_user(self, session: Session, token: str) -> bool:
        """Logout user by revoking token"""
        return self.token_crud.revoke_token(session=session, token=token)

    def log_security_event(
        self,
        session: Session,
        user_id: Optional[UUID],
        event_type: str,
        event_status: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> SecurityLog:
        """Log security event"""
        security_log = SecurityLog(
            user_id=user_id,
            event_type=event_type,
            event_status=event_status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            error_message=error_message,
        )

        session.add(security_log)
        session.commit()
        session.refresh(security_log)

        return security_log

    async def is_refresh_token_valid(
        self, session: Session, refresh_token: str
    ) -> bool:
        """Check if refresh token is valid"""
        token_obj = session.exec(
            select(Token).where(
                Token.token == refresh_token,
                Token.token_type == TokenType.refresh,
                Token.status == TokenStatus.active,
            )
        ).first()

        return token_obj is not None and not token_obj.is_expired()

    async def revoke_refresh_token(self, session: Session, refresh_token: str) -> bool:
        """Revoke refresh token"""
        token_obj = session.exec(
            select(Token).where(
                Token.token == refresh_token, Token.token_type == TokenType.refresh
            )
        ).first()

        if token_obj:
            token_obj.deactivate()
            session.commit()
            return True
        return False

    async def revoke_all_user_tokens(self, session: Session, user_id: UUID) -> bool:
        """Revoke all tokens for a user"""
        tokens = session.exec(
            select(Token).where(
                Token.user_id == user_id, Token.status == TokenStatus.active
            )
        ).all()

        for token in tokens:
            token.deactivate()

        session.commit()
        return True

    async def get_security_settings(
        self, session: Session, user_id: UUID
    ) -> SecuritySettings:
        """Get security settings for user"""
        credentials = session.exec(
            select(UserCredentials).where(UserCredentials.user_id == user_id)
        ).first()

        if not credentials:
            # Return default settings
            return SecuritySettings()

        return SecuritySettings(
            two_factor_enabled=credentials.two_factor_enabled,
            login_notifications=True,  # Default
            new_device_alerts=True,  # Default
            max_failed_attempts=5,  # Default
        )

    async def update_security_settings(
        self, session: Session, user_id: UUID, settings: SecuritySettings
    ) -> SecuritySettings:
        """Update security settings for user"""
        credentials = session.exec(
            select(UserCredentials).where(UserCredentials.user_id == user_id)
        ).first()

        if credentials:
            credentials.two_factor_enabled = settings.two_factor_enabled
            session.commit()
            session.refresh(credentials)

        return settings

    async def get_security_logs(
        self, session: Session, user_id: UUID, page: int = 1, per_page: int = 20
    ) -> SecurityLogsResponse:
        """Get security logs for user"""
        offset = (page - 1) * per_page

        logs = session.exec(
            select(SecurityLog)
            .where(SecurityLog.user_id == user_id)
            .order_by(desc(SecurityLog.created_at))
            .offset(offset)
            .limit(per_page)
        ).all()

        total_query = select(SecurityLog).where(SecurityLog.user_id == user_id)
        total = len(session.exec(total_query).all())

        # Convert model objects to schema objects
        schema_logs = []
        for log in logs:
            schema_logs.append(
                SecurityLog(
                    id=log.id,
                    event_type=log.event_type,
                    event_status=log.event_status,
                    ip_address=log.ip_address,
                    user_agent=log.user_agent,
                    country=log.country,
                    city=log.city,
                    details=log.details,
                    error_message=log.error_message,
                    created_at=log.created_at,
                )
            )

        return SecurityLogsResponse(
            logs=schema_logs, total=total, page=page, per_page=per_page
        )

    async def get_login_devices(self, session: Session, user_id: UUID) -> DeviceList:
        """Get login devices for user"""
        # This is a simplified implementation
        # In a real app, you'd track device information in a separate table
        devices = [
            LoginDevice(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                device_info=DeviceInfo(device_type="desktop", os="macOS"),
                login_at=datetime.utcnow(),
                last_active_at=datetime.utcnow(),
                is_current_device=True,
            )
        ]

        return DeviceList(devices=devices, total=len(devices))

    async def revoke_device(
        self, session: Session, user_id: UUID, device_id: UUID
    ) -> bool:
        """Revoke access for a specific device"""
        # Simplified implementation
        return True


# Create service instance
auth_service = AuthService()
