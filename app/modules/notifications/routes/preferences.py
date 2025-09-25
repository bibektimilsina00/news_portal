from fastapi import APIRouter, HTTPException
from sqlmodel import Session

from app.modules.notifications.crud.crud_preference import crud_notification_preference
from app.modules.notifications.schema.preference import (
    NotificationPreferencePublic,
    NotificationPreferenceUpdate,
)
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/", response_model=NotificationPreferencePublic)
def read_notification_preferences(
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get user's notification preferences"""
    preferences = crud_notification_preference.get_by_user(
        session=session, user_id=str(current_user.id)
    )
    if not preferences:
        # Create default preferences if none exist
        preferences = crud_notification_preference.create_or_update(
            session=session,
            user_id=str(current_user.id),
            obj_in=NotificationPreferenceUpdate(),
        )
    return preferences


@router.put("/", response_model=NotificationPreferencePublic)
def update_notification_preferences(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    preferences_in: NotificationPreferenceUpdate,
):
    """Update user's notification preferences"""
    preferences = crud_notification_preference.create_or_update(
        session=session,
        user_id=str(current_user.id),
        obj_in=preferences_in,
    )
    return preferences


@router.post("/reset")
def reset_notification_preferences(
    session: SessionDep,
    current_user: CurrentUser,
):
    """Reset notification preferences to defaults"""
    preferences = crud_notification_preference.reset_to_defaults(
        session=session, user_id=str(current_user.id)
    )
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return {"message": "Preferences reset to defaults"}
