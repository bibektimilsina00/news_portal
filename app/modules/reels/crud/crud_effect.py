import uuid
from typing import List, Optional

from sqlmodel import Session, select

from app.modules.reels.model.effect import Effect, EffectCategory
from app.modules.reels.schema.effect import EffectCreate, EffectUpdate
from app.shared.crud.base import CRUDBase


class CRUDEffect(CRUDBase[Effect, EffectCreate, EffectUpdate]):
    """CRUD operations for effects"""

    def get_by_category(
        self,
        session: Session,
        *,
        category: EffectCategory,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Effect]:
        """Get effects by category"""
        statement = (
            select(Effect)
            .where(Effect.category == category)
            .order_by(Effect.use_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def get_popular(self, session: Session, *, limit: int = 50) -> List[Effect]:
        """Get popular effects"""
        statement = select(Effect).order_by(Effect.use_count.desc()).limit(limit)
        return list(session.exec(statement))

    def get_premium(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Effect]:
        """Get premium effects"""
        statement = (
            select(Effect)
            .where(Effect.is_premium == True)
            .order_by(Effect.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def search_effects(
        self, session: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Effect]:
        """Search effects by name"""
        search_term = f"%{query}%"
        statement = (
            select(Effect)
            .where(Effect.name.ilike(search_term))
            .order_by(Effect.use_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement))

    def update_use_count(
        self, session: Session, *, effect_id: uuid.UUID
    ) -> Optional[Effect]:
        """Increment effect use count"""
        effect = self.get(session, id=effect_id)
        if not effect:
            return None

        effect.use_count += 1
        session.commit()
        session.refresh(effect)
        return effect


crud_effect = CRUDEffect(Effect)
