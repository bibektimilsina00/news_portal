"""
Two-factor authentication service for handling 2FA operations
"""

import json
import secrets
from typing import List, Optional
from uuid import UUID

import pyotp
from sqlmodel import Session, select

from app.modules.auth.crud.crud_auth import CRUDAuth
from app.modules.auth.model.auth import UserCredentials


class TwoFactorService:
    """Service for two-factor authentication operations"""

    def __init__(self):
        self.auth_crud = CRUDAuth()
        # Simple in-memory cache for temporary secrets (in production, use Redis/cache)
        self._temp_secrets = {}

    def generate_backup_codes(self) -> List[str]:
        """Generate 10 backup codes for 2FA"""
        backup_codes = []
        for _ in range(10):
            # Generate 8-character alphanumeric codes
            code = "".join(
                secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8)
            )
            backup_codes.append(code)
        return backup_codes

    async def store_temp_secret(
        self, session: Session, user_id: UUID, secret: str, backup_codes: List[str]
    ) -> None:
        """Store temporary 2FA secret and backup codes during setup"""
        # Store in memory cache with user_id as key
        self._temp_secrets[str(user_id)] = {
            "secret": secret,
            "backup_codes": backup_codes,
        }

    async def get_temp_secret(self, session: Session, user_id: UUID) -> Optional[dict]:
        """Get temporary 2FA secret and backup codes"""
        return self._temp_secrets.get(str(user_id))

    async def enable_two_factor(
        self, session: Session, user_id: UUID, secret: str, backup_codes: List[str]
    ) -> None:
        """Enable 2FA for user and store backup codes"""

        # Get user credentials
        credentials = session.exec(
            select(UserCredentials).where(UserCredentials.user_id == user_id)
        ).first()

        if not credentials:
            raise ValueError("User credentials not found")

        # Update credentials with 2FA data
        credentials.two_factor_enabled = True
        credentials.two_factor_secret = secret
        credentials.backup_codes = json.dumps(backup_codes)

        session.add(credentials)
        session.commit()
        session.refresh(credentials)

        # Clear temporary secret
        self._temp_secrets.pop(str(user_id), None)

    async def verify_backup_code(
        self, session: Session, user_id: UUID, code: str
    ) -> bool:
        """Verify a backup code and remove it from the list"""

        # Get user credentials
        credentials = session.exec(
            select(UserCredentials).where(UserCredentials.user_id == user_id)
        ).first()

        if not credentials or not credentials.backup_codes:
            return False

        try:
            backup_codes = json.loads(credentials.backup_codes)
        except json.JSONDecodeError:
            return False

        # Check if code exists
        if code in backup_codes:
            # Remove the used code
            backup_codes.remove(code)
            credentials.backup_codes = json.dumps(backup_codes)
            session.add(credentials)
            session.commit()
            return True

        return False

    async def disable_two_factor(self, session: Session, user_id: UUID) -> None:
        """Disable 2FA for user"""

        # Get user credentials
        credentials = session.exec(
            select(UserCredentials).where(UserCredentials.user_id == user_id)
        ).first()

        if not credentials:
            raise ValueError("User credentials not found")

        # Disable 2FA
        credentials.two_factor_enabled = False
        credentials.two_factor_secret = None
        credentials.backup_codes = None

        session.add(credentials)
        session.commit()
        session.refresh(credentials)

    async def get_backup_codes(
        self, session: Session, user_id: UUID
    ) -> Optional[List[str]]:
        """Get remaining backup codes for user"""

        # Get user credentials
        credentials = session.exec(
            select(UserCredentials).where(UserCredentials.user_id == user_id)
        ).first()

        if not credentials or not credentials.backup_codes:
            return None

        try:
            return json.loads(credentials.backup_codes)
        except json.JSONDecodeError:
            return None

    async def update_backup_codes(
        self, session: Session, user_id: UUID, backup_codes: List[str]
    ) -> None:
        """Update backup codes for user"""

        # Get user credentials
        credentials = session.exec(
            select(UserCredentials).where(UserCredentials.user_id == user_id)
        ).first()

        if not credentials:
            raise ValueError("User credentials not found")

        credentials.backup_codes = json.dumps(backup_codes)
        session.add(credentials)
        session.commit()
        session.refresh(credentials)

    def verify_totp_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code against secret"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()


# Create service instance
two_factor_service = TwoFactorService()
