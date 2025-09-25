import uuid
from datetime import datetime, timedelta
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import and_
from sqlmodel import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.modules.auth.crud.crud_auth import auth
from app.modules.auth.crud.crud_token import token
from app.modules.auth.model.auth import SecurityLog, UserCredentials
from app.modules.auth.model.token import Token, TokenType
from app.modules.auth.schema.auth import (
    APITokenCreate,
    APITokenList,
    APITokenResponse,
    DeviceInfo,
    DeviceList,
    EmailVerificationConfirm,
    EmailVerificationRequest,
    EmailVerificationResponse,
    LoginDevice,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    SecurityLog,
    SecurityLogsResponse,
    SecuritySettings,
    Token as TokenSchema,
    TokenPayload,
    TokenRevokeRequest,
    TokenRevokeResponse,
    TwoFactorResponse,
    TwoFactorSetup,
    TwoFactorVerify,
    UserLogin,
    UserLoginResponse,
)
from app.modules.auth.services.auth_service import auth_service
from app.modules.users.model.user import User
from app.modules.users.services.user_service import user_service
from app.shared.deps.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_user,
    get_current_user_optional,
)
from app.shared.exceptions.exceptions import (
    AccountDisabledException,
    AccountNotVerifiedException,
    InvalidCredentialsException,
    TokenExpiredException,
    TokenInvalidException,
    UnauthorizedException,
    UserNotFoundException,
)
from app.shared.schema.message import Message

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login", response_model=UserLoginResponse)
async def login(
    response: Response,
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
    device_info: Optional[DeviceInfo] = None,
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Authenticate user
    user = auth_service.authenticate_user(
        session=session, login=form_data.username, password=form_data.password
    )

    if not user:
        # Log failed login attempt
        await auth_service.log_security_event(
            session=session,
            event_type="failed_login",
            event_status="failed",
            ip_address=x_forwarded_for,
            user_agent=user_agent,
            details=f"Failed login attempt for {form_data.username}",
        )
        raise InvalidCredentialsException("Incorrect email/username or password")

    # Check if account is active
    if not user_service.is_active(user):
        raise AccountDisabledException("Account is disabled")

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = auth.create_access_token(
        subject=str(user.id),
        additional_claims={
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "account_type": user.account_type,
        },
    )

    refresh_token = auth.create_refresh_token(subject=str(user.id))

    # Store refresh token in database
    token_record = token.create_token(
        session=session,
        user_id=user.id,
        token=refresh_token,
        token_type=TokenType.REFRESH,
        expires_at=datetime.utcnow() + refresh_token_expires,
    )

    # Log successful login
    await auth_service.log_security_event(
        session=session,
        user_id=user.id,
        event_type="login",
        event_status="success",
        ip_address=x_forwarded_for,
        user_agent=user_agent,
        details="User logged in successfully",
    )

    # Update last login
    user_service.update_last_active(session=session, user_id=user.id)

    # Set secure cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return UserLoginResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        is_verified=user.is_verified,
        account_type=user.account_type,
        requires_two_factor=False,  # Implement 2FA check later
    )


@router.post("/login/json", response_model=UserLoginResponse)
async def login_json(
    response: Response,
    session: SessionDep,
    login_data: UserLogin,
    user_agent: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None),
) -> Any:
    """
    JSON-based login for mobile apps and modern web apps
    """
    user = auth_service.authenticate_user(
        session=session,
        login=login_data.username_or_email,
        password=login_data.password,
    )

    if not user:
        await auth_service.log_security_event(
            session=session,
            event_type="failed_login",
            event_status="failed",
            ip_address=x_forwarded_for,
            user_agent=user_agent,
            details=f"Failed login attempt for {login_data.username_or_email}",
        )
        raise InvalidCredentialsException("Incorrect email/username or password")

    if not user_service.is_active(user):
        raise AccountDisabledException("Account is disabled")

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = auth.create_access_token(
        subject=str(user.id),
        additional_claims={
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "account_type": user.account_type,
        },
    )

    refresh_token = auth.create_refresh_token(subject=str(user.id))

    # Store refresh token
    token.create_token(
        session=session,
        user_id=user.id,
        token=refresh_token,
        token_type=TokenType.REFRESH,
        expires_at=datetime.utcnow() + refresh_token_expires,
        user_agent=user_agent,
        ip_address=x_forwarded_for,
    )

    await auth_service.log_security_event(
        session=session,
        user_id=user.id,
        event_type="login",
        event_status="success",
        ip_address=x_forwarded_for,
        user_agent=user_agent,
        details="User logged in successfully via JSON",
    )

    user_service.update_last_active(session=session, user_id=user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return UserLoginResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        is_verified=user.is_verified,
        account_type=user.account_type,
        requires_two_factor=False,
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    response: Response,
    session: SessionDep,
    refresh_request: RefreshTokenRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    """
    Refresh access token using refresh token
    """
    # Get refresh token from request or cookie
    refresh_token = refresh_request.refresh_token

    if not refresh_token:
        raise TokenInvalidException("Refresh token is required")

    # Verify refresh token
    user_id = auth.verify_token(refresh_token, token_type="refresh")
    if not user_id:
        raise TokenInvalidException("Invalid refresh token")

    # Get user
    user = user_service.get_user_by_id(session=session, user_id=uuid.UUID(user_id))
    if not user:
        raise UserNotFoundException("User not found")

    if not user_service.is_active(user):
        raise AccountDisabledException("Account is disabled")

    # Check if refresh token exists in database and is active
    if not await auth_service.is_refresh_token_valid(
        session=session, refresh_token=refresh_token
    ):
        raise TokenInvalidException("Refresh token has been revoked")

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = auth.create_access_token(
        subject=str(user.id),
        additional_claims={
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "account_type": user.account_type,
        },
    )

    # Create new refresh token (token rotation)
    new_refresh_token = auth.create_refresh_token(subject=str(user.id))

    # Revoke old refresh token
    await auth_service.revoke_refresh_token(
        session=session, refresh_token=refresh_token
    )

    # Store new refresh token
    token.create_token(
        session=session,
        user_id=user.id,
        token=new_refresh_token,
        token_type=TokenType.REFRESH,
        expires_at=datetime.utcnow()
        + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )

    # Update last active
    user_service.update_last_active(session=session, user_id=user.id)

    # Set new refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return RefreshTokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout")
async def logout(
    response: Response,
    session: SessionDep,
    refresh_request: RefreshTokenRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Logout user and revoke tokens
    """
    refresh_token = refresh_request.refresh_token

    if refresh_token:
        # Revoke refresh token
        await auth_service.revoke_refresh_token(
            session=session, refresh_token=refresh_token
        )

        # Revoke all access tokens for user (optional)
        await auth_service.revoke_all_user_tokens(
            session=session, user_id=current_user.id
        )

    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token")

    # Log logout event
    await auth_service.log_security_event(
        session=session,
        user_id=current_user.id,
        event_type="logout",
        event_status="success",
        details="User logged out successfully",
    )

    return Message(message="Logged out successfully")


@router.post("/password-reset/request", response_model=Message)
async def request_password_reset(
    session: SessionDep, reset_request: PasswordResetRequest
) -> Any:
    """
    Request password reset email
    """
    user = user_service.get_user_by_email(session=session, email=reset_request.email)

    if not user:
        # Don't reveal if user exists or not
        return Message(
            message="If an account exists with this email, you will receive a password reset link"
        )

    if not user_service.is_active(user):
        return Message(
            message="If an account exists with this email, you will receive a password reset link"
        )

    # Generate password reset token
    reset_token = auth.create_password_reset_token(email=reset_request.email)

    # Store token in database
    from app.modules.authentication.model.auth import PasswordResetToken

    reset_token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=datetime.utcnow()
        + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )
    session.add(reset_token_record)
    session.commit()

    # Send password reset email (implement email service)
    # await email_service.send_password_reset_email(user.email, reset_token)

    # Log password reset request
    await auth_service.log_security_event(
        session=session,
        user_id=user.id,
        event_type="password_reset_requested",
        event_status="success",
        details="Password reset requested",
    )

    return Message(
        message="If an account exists with this email, you will receive a password reset link"
    )


@router.post("/password-reset/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(
    session: SessionDep, reset_confirm: PasswordResetConfirm
) -> Any:
    """
    Confirm password reset with token
    """
    # Verify reset token
    email = auth.verify_password_reset_token(reset_confirm.token)
    if not email:
        raise TokenInvalidException("Invalid or expired password reset token")

    # Get user by email
    user = user_service.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFoundException("User not found")

    # Check if token exists and is valid
    from app.modules.authentication.model.auth import PasswordResetToken

    token_record = session.exec(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.token == reset_confirm.token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > datetime.utcnow(),
            )
        )
    ).first()

    if not token_record:
        raise TokenInvalidException("Invalid or expired password reset token")

    # Update user password
    user_service.update_user(
        session=session, db_user=user, user_in={"password": reset_confirm.new_password}
    )

    # Mark token as used
    token_record.used = True
    token_record.used_at = datetime.utcnow()
    session.add(token_record)
    session.commit()

    # Log password reset success
    await auth_service.log_security_event(
        session=session,
        user_id=user.id,
        event_type="password_reset_completed",
        event_status="success",
        details="Password reset completed successfully",
    )

    return PasswordResetResponse(message="Password reset successful", success=True)


@router.post("/email/verify/request", response_model=Message)
async def request_email_verification(
    session: SessionDep, current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Request email verification
    """
    if current_user.email_verified:
        return Message(message="Email already verified")

    # Generate verification token
    verification_token = auth.create_email_verification_token(email=current_user.email)

    # Store token in database
    from app.modules.authentication.model.auth import EmailVerificationToken

    verification_record = EmailVerificationToken(
        user_id=current_user.id,
        email=current_user.email,
        token=verification_token,
        expires_at=datetime.utcnow()
        + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS),
    )
    session.add(verification_record)
    session.commit()

    # Send verification email (implement email service)
    # await email_service.send_verification_email(current_user.email, verification_token)

    return Message(message="Verification email sent")


@router.post("/email/verify/confirm", response_model=EmailVerificationResponse)
async def confirm_email_verification(
    session: SessionDep, verification_confirm: EmailVerificationConfirm
) -> Any:
    """
    Confirm email verification
    """
    # Verify token
    email = auth.verify_email_verification_token(verification_confirm.token)
    if not email:
        raise TokenInvalidException("Invalid or expired verification token")

    # Find user by email
    user = user_service.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFoundException("User not found")

    # Check if token exists and is valid
    from app.modules.authentication.model.auth import EmailVerificationToken

    token_record = session.exec(
        select(EmailVerificationToken).where(
            and_(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.token == verification_confirm.token,
                EmailVerificationToken.used == False,
                EmailVerificationToken.expires_at > datetime.utcnow(),
            )
        )
    ).first()

    if not token_record:
        raise TokenInvalidException("Invalid or expired verification token")

    # Mark email as verified
    user_service.update_user(
        session=session, db_user=user, user_in={"email_verified": True}
    )

    # Mark token as used
    token_record.used = True
    token_record.used_at = datetime.utcnow()
    session.add(token_record)
    session.commit()

    return EmailVerificationResponse(
        message="Email verified successfully", success=True, email_verified=True
    )


@router.get("/security/settings", response_model=SecuritySettings)
async def get_security_settings(
    session: SessionDep, current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get user security settings
    """
    return await auth_service.get_security_settings(
        session=session, user_id=current_user.id
    )


@router.patch("/security/settings", response_model=SecuritySettings)
async def update_security_settings(
    session: SessionDep,
    settings_update: SecuritySettings,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update user security settings
    """
    return await auth_service.update_security_settings(
        session=session, user_id=current_user.id, settings=settings_update
    )


@router.get("/security/logs", response_model=SecurityLogsResponse)
async def get_security_logs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user security logs
    """
    logs = await auth_service.get_security_logs(
        session=session, user_id=current_user.id, skip=skip, limit=limit
    )

    return SecurityLogsResponse(
        logs=logs, total=len(logs), page=skip // limit, per_page=limit
    )


@router.get("/devices", response_model=DeviceList)
async def get_login_devices(
    session: SessionDep, current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get login devices
    """
    devices = await auth_service.get_login_devices(
        session=session, user_id=current_user.id
    )

    return DeviceList(devices=devices, total=len(devices))


@router.delete("/devices/{device_id}")
async def revoke_device(
    session: SessionDep,
    device_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Revoke a login device
    """
    success = await auth_service.revoke_device(
        session=session, user_id=current_user.id, device_id=device_id
    )

    if not success:
        raise HTTPException(status_code=404, detail="Device not found")

    return Message(message="Device revoked successfully")


@router.post("/tokens/api", response_model=APITokenResponse)
async def create_api_token(
    session: SessionDep,
    token_create: APITokenCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create API token for programmatic access
    """
    # Create API token
    api_token = auth.create_api_token(
        user_id=current_user.id,
        name=token_create.name,
        expires_delta=timedelta(days=token_create.expires_in_days),
    )

    # Store in database
    from app.modules.authentication.model.token import APIToken

    db_token = APIToken(
        user_id=current_user.id,
        name=token_create.name,
        token=api_token,
        prefix=api_token[:8],  # First 8 characters for identification
        permissions=token_create.permissions,
        expires_at=datetime.utcnow() + timedelta(days=token_create.expires_in_days),
    )
    session.add(db_token)
    session.commit()
    session.refresh(db_token)

    return APITokenResponse(
        id=db_token.id,
        name=db_token.name,
        token=api_token,
        prefix=db_token.prefix,
        permissions=db_token.permissions,
        is_active=db_token.is_active,
        expires_at=db_token.expires_at,
        created_at=db_token.created_at,
    )


@router.get("/tokens/api", response_model=APITokenList)
async def get_api_tokens(
    session: SessionDep,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user's API tokens
    """
    from app.modules.authentication.model.token import APIToken

    statement = (
        select(APIToken)
        .where(APIToken.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    tokens = session.exec(statement).all()

    token_responses = []
    for token_obj in tokens:
        token_responses.append(
            APITokenResponse(
                id=token_obj.id,
                name=token_obj.name,
                token="***",  # Hide actual token
                prefix=token_obj.prefix,
                permissions=token_obj.permissions,
                is_active=token_obj.is_active,
                last_used_at=token_obj.last_used_at,
                usage_count=token_obj.usage_count,
                expires_at=token_obj.expires_at,
                created_at=token_obj.created_at,
            )
        )

    return APITokenList(tokens=token_responses, total=len(token_responses))


@router.delete("/tokens/api/{token_id}")
async def revoke_api_token(
    session: SessionDep,
    token_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Revoke API token
    """
    from app.modules.authentication.model.token import APIToken

    token_obj = session.get(APIToken, token_id)
    if not token_obj or token_obj.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Token not found")

    token_obj.is_active = False
    session.add(token_obj)
    session.commit()

    return Message(message="API token revoked successfully")


@router.post("/tokens/revoke", response_model=TokenRevokeResponse)
async def revoke_token(
    session: SessionDep,
    revoke_request: TokenRevokeRequest,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Revoke any token (access or refresh)
    """
    success = await auth_service.revoke_token(
        session=session,
        user_id=current_user.id,
        token=revoke_request.token,
        reason=revoke_request.reason,
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to revoke token")

    return TokenRevokeResponse(success=True, message="Token revoked successfully")


@router.post("/logout/all")
async def logout_all_devices(
    response: Response,
    session: SessionDep,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Logout from all devices
    """
    # Revoke all tokens for user
    revoked_count = await auth_service.revoke_all_user_tokens(
        session=session, user_id=current_user.id
    )

    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token")

    # Log event
    await auth_service.log_security_event(
        session=session,
        user_id=current_user.id,
        event_type="logout_all",
        event_status="success",
        details=f"Logged out from all devices ({revoked_count} tokens revoked)",
    )

    return Message(
        message=f"Logged out from all devices ({revoked_count} tokens revoked)"
    )
