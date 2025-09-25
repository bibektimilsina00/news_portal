import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.users.schema.profile import (
    CloseFriendResponse,
    ProfileAnalytics,
    ProfileCreate,
    ProfilePrivate,
    ProfilePublic,
    ProfileUpdate,
    UserBlockResponse,
)
from app.modules.users.services import profile_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=ProfilePrivate)
def get_my_profile(
    *,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get current user's profile"""
    profile = profile_service.get_user_profile(session=session, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfilePrivate.model_validate(profile)


@router.post("/", response_model=ProfilePrivate)
def create_or_update_profile(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    profile_data: ProfileCreate,
):
    """Create or update user profile"""
    try:
        profile = profile_service.create_or_update_profile(
            session=session, user_id=current_user.id, profile_data=profile_data
        )
        return ProfilePrivate.model_validate(profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/", response_model=ProfilePrivate)
def update_profile(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    profile_data: ProfileUpdate,
):
    """Update user profile"""
    profile = profile_service.update_profile(
        session=session, user_id=current_user.id, profile_data=profile_data
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfilePrivate.model_validate(profile)


@router.get("/public/{user_id}", response_model=ProfilePublic)
def get_user_profile(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
):
    """Get public profile of another user"""
    profile = profile_service.get_user_profile(session=session, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfilePublic.model_validate(profile)


@router.post("/close-friends/{friend_id}")
def add_close_friend(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    friend_id: uuid.UUID,
):
    """Add a user to close friends list"""
    try:
        close_friend = profile_service.add_close_friend(
            session=session, user_id=current_user.id, friend_id=friend_id
        )
        return {
            "message": "User added to close friends",
            "close_friend_id": close_friend.id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/close-friends/{friend_id}")
def remove_close_friend(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    friend_id: uuid.UUID,
):
    """Remove a user from close friends list"""
    success = profile_service.remove_close_friend(
        session=session, user_id=current_user.id, friend_id=friend_id
    )
    if not success:
        raise HTTPException(
            status_code=404, detail="Close friend relationship not found"
        )
    return {"message": "User removed from close friends"}


@router.get("/close-friends", response_model=List[CloseFriendResponse])
def get_close_friends(
    *,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get current user's close friends"""
    close_friends = profile_service.get_close_friends(
        session=session, user_id=current_user.id
    )
    return [CloseFriendResponse.model_validate(cf) for cf in close_friends]


@router.post("/block/{user_id}")
def block_user(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
):
    """Block a user"""
    try:
        block = profile_service.block_user(
            session=session, blocker_id=current_user.id, blocked_id=user_id
        )
        return {"message": "User blocked", "block_id": block.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/block/{user_id}")
def unblock_user(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
):
    """Unblock a user"""
    success = profile_service.unblock_user(
        session=session, blocker_id=current_user.id, blocked_id=user_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"message": "User unblocked"}


@router.get("/blocked", response_model=List[UserBlockResponse])
def get_blocked_users(
    *,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get list of blocked users"""
    blocks = profile_service.get_blocked_users(session=session, user_id=current_user.id)
    return [UserBlockResponse.model_validate(block) for block in blocks]


@router.get("/analytics", response_model=ProfileAnalytics)
def get_profile_analytics(
    *,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get profile analytics"""
    analytics = profile_service.get_profile_analytics(
        session=session, user_id=current_user.id
    )
    return ProfileAnalytics.model_validate(analytics)


@router.post("/view/{profile_id}")
def record_profile_view(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    profile_id: uuid.UUID,
):
    """Record a profile view (for analytics)"""
    profile_service.record_profile_view(
        session=session, profile_id=profile_id, viewer_id=current_user.id
    )
    return {"message": "Profile view recorded"}
