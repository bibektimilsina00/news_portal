from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.modules.notifications.crud.crud_device import crud_device
from app.modules.notifications.schema.device import (
    DeviceCreate,
    DevicePublic,
    DeviceUpdate,
    DeviceWithUser,
)
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter()


@router.post("/", response_model=DevicePublic)
def create_device(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    device_in: DeviceCreate,
):
    """Register a new device for push notifications"""
    # Ensure the device belongs to the current user
    device_in.user_id = str(current_user.id)

    # Check if device token already exists
    existing_device = crud_device.get_by_token(
        session=session, device_token=device_in.device_token
    )
    if existing_device:
        if existing_device.user_id == str(current_user.id):
            # Update existing device
            update_data = device_in.model_dump(
                exclude={"user_id"}
            )  # Exclude user_id as it's already set
            device = crud_device.update(
                session=session, db_obj=existing_device, obj_in=update_data
            )
            return device
        else:
            raise HTTPException(
                status_code=400,
                detail="Device token already registered to another user",
            )

    device = crud_device.create(session=session, obj_in=device_in)
    return device


@router.get("/", response_model=List[DevicePublic])
def read_devices(
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get user's registered devices"""
    devices = crud_device.get_by_user(session=session, user_id=str(current_user.id))
    return devices


@router.get("/active", response_model=List[DevicePublic])
def read_active_devices(
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get user's active devices"""
    devices = crud_device.get_active_by_user(
        session=session, user_id=str(current_user.id)
    )
    return devices


@router.put("/{device_id}", response_model=DevicePublic)
def update_device(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    device_id: UUID,
    device_in: DeviceUpdate,
):
    """Update device information"""
    device = crud_device.get(session=session, id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    device = crud_device.update(session=session, db_obj=device, obj_in=device_in)
    return device


@router.put("/{device_id}/deactivate")
def deactivate_device(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    device_id: UUID,
):
    """Deactivate a device"""
    device = crud_device.get(session=session, id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    device = crud_device.deactivate_device(session=session, device_id=device_id)
    return {"message": "Device deactivated"}


@router.delete("/{device_id}")
def delete_device(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    device_id: UUID,
):
    """Delete a device registration"""
    device = crud_device.get(session=session, id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud_device.remove(session=session, id=device_id)
    return {"message": "Device deleted"}
