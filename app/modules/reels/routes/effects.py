import uuid
from typing import Any, List

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.reels.model.effect import EffectCategory
from app.modules.reels.schema.effect import (
    EffectCreate,
    EffectPublic,
    EffectUpdate,
)
from app.modules.reels.services.effect_service import effect_service
from app.shared.deps.deps import CurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter(prefix="/effects", tags=["reel-effects"])


@router.get("/", response_model=List[EffectPublic])
def get_effects_list(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
) -> Any:
    """
    Get list of all effects
    """
    effects = effect_service.get_effects_list(session=session, skip=skip, limit=limit)
    return effects


@router.get("/popular", response_model=List[EffectPublic])
def get_popular_effects(
    session: SessionDep,
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get popular effects
    """
    effects = effect_service.get_popular_effects(session=session, limit=limit)
    return effects


@router.get("/premium", response_model=List[EffectPublic])
def get_premium_effects(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get premium effects
    """
    effects = effect_service.get_premium_effects(
        session=session, skip=skip, limit=limit
    )
    return effects


@router.get("/category/{category}", response_model=List[EffectPublic])
def get_effects_by_category(
    session: SessionDep,
    category: EffectCategory,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get effects by category
    """
    effects = effect_service.get_effects_by_category(
        session=session, category=category, skip=skip, limit=limit
    )
    return effects


@router.get("/search", response_model=List[EffectPublic])
def search_effects(
    session: SessionDep,
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Search effects by name
    """
    effects = effect_service.search_effects(
        session=session, query=q, skip=skip, limit=limit
    )
    return effects


@router.post("/", response_model=EffectPublic)
def create_effect(
    session: SessionDep,
    current_user: CurrentUser,
    effect_in: EffectCreate,
) -> Any:
    """
    Create a new effect (admin only)
    """
    # TODO: Add admin check
    effect = effect_service.create_effect(session=session, effect_in=effect_in)
    return effect


@router.get("/{effect_id}", response_model=EffectPublic)
def get_effect(
    session: SessionDep,
    effect_id: uuid.UUID,
) -> Any:
    """
    Get a specific effect
    """
    effect = effect_service.get_effect(session=session, effect_id=effect_id)
    if not effect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Effect not found",
        )
    return effect


@router.put("/{effect_id}", response_model=EffectPublic)
def update_effect(
    session: SessionDep,
    current_user: CurrentUser,
    effect_id: uuid.UUID,
    effect_in: EffectUpdate,
) -> Any:
    """
    Update an effect (admin only)
    """
    # TODO: Add admin check
    effect = effect_service.update_effect(
        session=session, effect_id=effect_id, effect_in=effect_in
    )
    if not effect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Effect not found",
        )
    return effect


@router.delete("/{effect_id}", response_model=Message)
def delete_effect(
    session: SessionDep,
    current_user: CurrentUser,
    effect_id: uuid.UUID,
) -> Any:
    """
    Delete an effect (admin only)
    """
    # TODO: Add admin check
    success = effect_service.delete_effect(session=session, effect_id=effect_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Effect not found",
        )
    return Message(message="Effect deleted successfully")


@router.post("/{effect_id}/use", response_model=Message)
def use_effect(
    session: SessionDep,
    current_user: CurrentUser,
    effect_id: uuid.UUID,
) -> Any:
    """
    Record effect usage (called when effect is applied to a reel)
    """
    effect = effect_service.increment_use_count(session=session, effect_id=effect_id)
    if not effect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Effect not found",
        )
    return Message(message="Effect usage recorded successfully")
