import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Session, and_, func, select

from app.modules.auth.model.token import Token, TokenStatus, TokenType
from app.modules.auth.schema.token import TokenCreate, TokenUpdate
from app.shared.crud.base import CRUDBase


class CRUDToken(CRUDBase[Token, TokenCreate, TokenUpdate]):
    """CRUD operations for token management (blacklisting, API tokens, etc.)"""

    def create_token(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        token: str,
        token_type: TokenType,
        name: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Token:
        """Create a new token record"""
        db_obj = Token(
            user_id=user_id,
            token=token,
            token_type=token_type,
            name=name,
            expires_at=expires_at,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_by_token(self, session: Session, *, token: str) -> Optional[Token]:
        """Get token by token string"""
        statement = select(Token).where(Token.token == token)
        return session.exec(statement).first()

    def get_user_tokens(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        token_type: Optional[TokenType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Token]:
        """Get all tokens for a user"""
        statement = select(Token).where(Token.user_id == user_id)

        if token_type:
            statement = statement.where(Token.token_type == token_type)

        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement))

    def get_active_tokens(
        self,
        session: Session,
        *,
        user_id: Optional[uuid.UUID] = None,
        token_type: Optional[TokenType] = None,
    ) -> List[Token]:
        """Get all active tokens"""
        statement = select(Token).where(
            and_(Token.is_active == True, Token.expires_at > func.now())
        )

        if user_id:
            statement = statement.where(Token.user_id == user_id)

        if token_type:
            statement = statement.where(Token.token_type == token_type)

        return list(session.exec(statement))

    def deactivate_token(
        self, session: Session, *, token_id: uuid.UUID
    ) -> Optional[Token]:
        """Deactivate a specific token"""
        db_obj = self.get(session=session, id=token_id)
        if db_obj:
            db_obj.status = TokenStatus.BLACKLISTED
            db_obj.deactivated_at = datetime.now(timezone.utc)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj

    def deactivate_user_tokens(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        token_type: Optional[TokenType] = None,
    ) -> int:
        """Deactivate all tokens for a user"""
        statement = select(Token).where(
            and_(Token.user_id == user_id, Token.is_active == True)
        )

        if token_type:
            statement = statement.where(Token.token_type == token_type)

        tokens = session.exec(statement)
        count = 0

        for token in tokens:
            token.status = TokenStatus.EXPIRED
            token.deactivated_at = datetime.now(timezone.utc)
            session.add(token)
            count += 1

        session.commit()
        return count

    def cleanup_expired_tokens(self, session: Session) -> int:
        """Remove expired tokens"""
        statement = select(Token).where(
            and_(Token.expires_at < func.now(), Token.status == TokenStatus.ACTIVE)
        )

        expired_tokens = session.exec(statement)
        count = 0

        for token in expired_tokens:
            token.status = TokenStatus.EXPIRED
            token.deactivated_at = datetime.now(timezone.utc)
            session.add(token)
            count += 1

        session.commit()
        return count

    def is_token_active(self, session: Session, *, token: str) -> bool:
        """Check if a token is active and not expired"""
        db_token = self.get_by_token(session=session, token=token)
        if not db_token:
            return False

        if not db_token.is_active:
            return False

        if db_token.expires_at and db_token.expires_at < datetime.now(timezone.utc):
            return False

        return True

    def revoke_token(self, session: Session, *, token: str) -> bool:
        """Revoke/blacklist a token"""
        db_token = self.get_by_token(session=session, token=token)
        if db_token:
            db_token.status = TokenStatus.REVOKED
            db_token.deactivated_at = datetime.now(timezone.utc)
            session.add(db_token)
            session.commit()
            return True
        return False

    def get_token_stats(self, session: Session, user_id: uuid.UUID) -> dict:
        """Get token statistics for a user"""
        total_tokens = session.exec(
            select(func.count(Token.id)).where(Token.user_id == user_id)
        ).one()

        active_tokens = session.exec(
            select(func.count(Token.id)).where(
                and_(Token.user_id == user_id, Token.status == TokenStatus.ACTIVE)
            )
        ).one()

        expired_tokens = session.exec(
            select(func.count(Token.id)).where(
                and_(Token.user_id == user_id, Token.expires_at < func.now())
            )
        ).one()

        return {
            "total_tokens": total_tokens,
            "active_tokens": active_tokens,
            "expired_tokens": expired_tokens,
        }


# Create singleton instance
token = CRUDToken(Token)
