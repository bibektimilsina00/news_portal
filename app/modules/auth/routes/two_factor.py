import base64
import uuid
from io import BytesIO
from typing import Any, Optional

import pyotp
import qrcode
from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.schema.auth import (
    TwoFactorResponse,
    TwoFactorSetup,
    TwoFactorVerify,
)
from app.modules.auth.services.two_factor_service import two_factor_service
from app.shared.deps.deps import ActiveCurrentUser, SessionDep
from app.shared.schema.message import Message

router = APIRouter(prefix="/2fa", tags=["two-factor"])


@router.post("/setup", response_model=TwoFactorSetup)
async def setup_two_factor(
    session: SessionDep,
    current_user: ActiveCurrentUser,
) -> Any:
    """
    Setup two-factor authentication
    """
    if current_user.credentials and current_user.credentials.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is already enabled",
        )

    # Generate secret
    secret = pyotp.random_base32()

    # Generate QR code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email, issuer_name="NewsGram"
    )

    # Create QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_data = base64.b64encode(buffer.getvalue()).decode()

    # Generate backup codes
    backup_codes = two_factor_service.generate_backup_codes()

    # Store secret temporarily (will be confirmed later)
    await two_factor_service.store_temp_secret(
        session=session,
        user_id=current_user.id,
        secret=secret,
        backup_codes=backup_codes,
    )

    return TwoFactorSetup(
        secret=secret, qr_code=qr_code_data, backup_codes=backup_codes
    )


@router.post("/verify-setup", response_model=TwoFactorResponse)
async def verify_two_factor_setup(
    session: SessionDep,
    verification: TwoFactorVerify,
    current_user: ActiveCurrentUser,
) -> Any:
    """
    Verify two-factor setup with code
    """
    # Get temp secret
    temp_data = await two_factor_service.get_temp_secret(
        session=session, user_id=current_user.id
    )
    if not temp_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No two-factor setup in progress",
        )

    secret = temp_data["secret"]
    backup_codes = temp_data["backup_codes"]

    # Verify code
    totp = pyotp.TOTP(secret)
    is_valid = totp.verify(verification.code, valid_window=1)

    if not is_valid:
        # Check if it's a backup code
        if verification.code in backup_codes:
            backup_codes.remove(verification.code)
            is_valid = True
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

    # Enable two-factor authentication
    await two_factor_service.enable_two_factor(
        session=session,
        user_id=current_user.id,
        secret=secret,
        backup_codes=backup_codes,
    )

    return TwoFactorResponse(enabled=True, backup_codes=backup_codes)


@router.post("/verify", response_model=dict)
async def verify_two_factor(
    session: SessionDep,
    verification: TwoFactorVerify,
    current_user: ActiveCurrentUser,
) -> Any:
    """
    Verify two-factor authentication code
    """
    if not current_user.credentials or not current_user.credentials.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is not enabled",
        )

    secret = current_user.credentials.two_factor_secret
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication secret not found",
        )

    # Verify code
    totp = pyotp.TOTP(secret)
    is_valid = totp.verify(verification.code, valid_window=1)

    if not is_valid:
        # Check backup codes
        is_backup_code = await two_factor_service.verify_backup_code(
            session=session, user_id=current_user.id, code=verification.code
        )

        if not is_backup_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

    return {"valid": True, "message": "Verification successful"}


@router.post("/disable", response_model=Message)
async def disable_two_factor(
    session: SessionDep,
    verification: TwoFactorVerify,
    current_user: ActiveCurrentUser,
) -> Any:
    """
    Disable two-factor authentication
    """
    if not current_user.credentials or not current_user.credentials.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is not enabled",
        )

    secret = current_user.credentials.two_factor_secret
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication secret not found",
        )

    # Verify code before disabling
    totp = pyotp.TOTP(secret)
    is_valid = totp.verify(verification.code, valid_window=1)

    if not is_valid:
        # Check backup codes
        is_backup_code = await two_factor_service.verify_backup_code(
            session=session, user_id=current_user.id, code=verification.code
        )

        if not is_backup_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

    # Disable two-factor authentication
    await two_factor_service.disable_two_factor(
        session=session, user_id=current_user.id
    )

    return Message(message="Two-factor authentication disabled successfully")


@router.get("/backup-codes", response_model=dict)
async def get_backup_codes(
    session: SessionDep,
    current_user: ActiveCurrentUser,
) -> Any:
    """
    Get remaining backup codes
    """
    if not current_user.credentials or not current_user.credentials.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is not enabled",
        )

    backup_codes = await two_factor_service.get_backup_codes(
        session=session, user_id=current_user.id
    )

    return {"backup_codes": backup_codes, "remaining": len(backup_codes)}


@router.post("/backup-codes/regenerate", response_model=dict)
async def regenerate_backup_codes(
    session: SessionDep,
    verification: TwoFactorVerify,
    current_user: ActiveCurrentUser,
) -> Any:
    """
    Regenerate backup codes
    """
    if not current_user.credentials or not current_user.credentials.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is not enabled",
        )

    secret = current_user.credentials.two_factor_secret
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication secret not found",
        )

    # Verify code before regenerating
    totp = pyotp.TOTP(secret)
    is_valid = totp.verify(verification.code, valid_window=1)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
        )

    # Generate new backup codes
    new_backup_codes = two_factor_service.generate_backup_codes()

    # Update backup codes
    await two_factor_service.update_backup_codes(
        session=session, user_id=current_user.id, backup_codes=new_backup_codes
    )

    return {
        "backup_codes": new_backup_codes,
        "message": "Backup codes regenerated successfully",
    }


@router.get("/status", response_model=TwoFactorResponse)
async def get_two_factor_status(
    current_user: ActiveCurrentUser,
) -> Any:
    """
    Get two-factor authentication status
    """
    enabled = (
        current_user.credentials
        and current_user.credentials.two_factor_enabled
        and current_user.credentials.two_factor_secret
    )

    return TwoFactorResponse(enabled=enabled)
