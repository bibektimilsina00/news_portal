import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.modules.reels.crud.crud_effect import crud_effect
from app.modules.reels.model.effect import Effect, EffectCategory
from app.modules.reels.schema.effect import EffectCreate, EffectUpdate
from app.shared.deps.deps import SessionDep


class EffectService:
    """Service layer for effect operations"""

    @staticmethod
    def get_effect(session: SessionDep, effect_id: uuid.UUID) -> Optional[Effect]:
        """Get effect by ID"""
        return crud_effect.get(session, id=effect_id)

    @staticmethod
    def get_effects_list(
        session: SessionDep, skip: int = 0, limit: int = 100
    ) -> List[Effect]:
        """Get list of all effects"""
        return crud_effect.get_multi(session, skip=skip, limit=limit)

    @staticmethod
    def create_effect(session: SessionDep, effect_in: EffectCreate) -> Effect:
        """Create new effect"""
        return crud_effect.create(session, obj_in=effect_in)

    @staticmethod
    def update_effect(
        session: SessionDep, effect_id: uuid.UUID, effect_in: EffectUpdate
    ) -> Optional[Effect]:
        """Update effect"""
        effect = crud_effect.get(session, id=effect_id)
        if not effect:
            return None

        return crud_effect.update(session, db_obj=effect, obj_in=effect_in)

    @staticmethod
    def delete_effect(session: SessionDep, effect_id: uuid.UUID) -> bool:
        """Delete effect"""
        effect = crud_effect.get(session, id=effect_id)
        if not effect:
            return False

        crud_effect.remove(session, id=effect_id)
        return True

    @staticmethod
    def get_effects_by_category(
        session: SessionDep, category: EffectCategory, skip: int = 0, limit: int = 100
    ) -> List[Effect]:
        """Get effects by category"""
        return crud_effect.get_by_category(
            session, category=category, skip=skip, limit=limit
        )

    @staticmethod
    def get_popular_effects(session: SessionDep, limit: int = 50) -> List[Effect]:
        """Get popular effects"""
        return crud_effect.get_popular(session, limit=limit)

    @staticmethod
    def get_premium_effects(
        session: SessionDep, skip: int = 0, limit: int = 100
    ) -> List[Effect]:
        """Get premium effects"""
        return crud_effect.get_premium(session, skip=skip, limit=limit)

    @staticmethod
    def search_effects(
        session: SessionDep, query: str, skip: int = 0, limit: int = 100
    ) -> List[Effect]:
        """Search effects by name"""
        return crud_effect.search_effects(session, query=query, skip=skip, limit=limit)

    @staticmethod
    def increment_use_count(
        session: SessionDep, effect_id: uuid.UUID
    ) -> Optional[Effect]:
        """Increment effect use count when applied to a reel"""
        return crud_effect.update_use_count(session, effect_id=effect_id)


effect_service = EffectService()
