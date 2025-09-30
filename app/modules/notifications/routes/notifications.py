from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.modules.notifications.schema.notification import (
    NotificationWithSender,
)
from app.modules.notifications.services.notification_service import notification_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/", response_model=List[NotificationWithSender])
def read_notifications(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_read: bool = Query(True),
):
    """Get user's notifications"""
    notifications = notification_service.get_user_notifications(
        session=session,
        user_id=str(current_user.id),
        skip=skip,
        limit=limit,
        include_read=include_read,
    )
    return notifications


@router.get("/unread/count")
def get_unread_count(session: SessionDep, current_user: CurrentUser):
    """Get count of unread notifications"""
    count = notification_service.get_unread_count(
        session=session, user_id=str(current_user.id)
    )
    return {"unread_count": count}


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Mark a notification as read"""
    notification = notification_service.mark_as_read(
        session=session,
        notification_id=notification_id,
        user_id=str(current_user.id),
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@router.put("/read-all")
def mark_all_notifications_as_read(
    session: SessionDep,
    current_user: CurrentUser,
):
    """Mark all notifications as read"""
    count = notification_service.mark_all_as_read(
        session=session, user_id=str(current_user.id)
    )
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Delete a notification (soft delete by marking as read)"""
    # For now, just mark as read. In a real app, you might want actual deletion
    notification = notification_service.mark_as_read(
        session=session,
        notification_id=notification_id,
        user_id=str(current_user.id),
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}
