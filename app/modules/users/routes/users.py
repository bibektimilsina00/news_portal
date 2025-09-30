import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from app.core.config import settings
from app.core.security import verify_password
from app.modules.users.model.user import AccountType, User
from app.modules.users.schema.user import (
    UpdatePassword,
    UserCreate,
    UserPrivate,
    UserProfilePublic,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserStats,
    UserUpdate,
    UserUpdateMe,
    VerificationRequest,
)
from app.modules.users.services.user_service import user_service
from app.shared.deps.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.shared.schema.message import Message
from app.shared.utils.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    account_type: Optional[AccountType] = None,
    is_verified: Optional[bool] = None,
    is_journalist: Optional[bool] = None,
) -> Any:
    """
    Retrieve users with optional filtering.
    Superuser only endpoint.
    """
    query = select(User)

    # Apply filters
    if account_type:
        query = query.where(User.account_type == account_type)
    if is_verified is not None:
        query = query.where(User.is_verified == is_verified)
    if is_journalist is not None:
        query = query.where(User.is_journalist == is_journalist)

    count = len(list(session.exec(query)))
    users = session.exec(query.offset(skip).limit(limit)).all()

    users_public = [UserPublic.model_validate(user) for user in users]
    return UsersPublic(data=users_public, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user (Superuser only).
    """
    # Check if email already exists
    user = user_service.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    # Check if username already exists
    user = user_service.get_user_by_username(session=session, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )

    user = user_service.create_user(session=session, user_create=user_in)

    # Send welcome email if enabled
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.username, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without authentication (Public endpoint).
    """
    # Check if email already exists
    user = user_service.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )

    # Check if username already exists
    user = user_service.get_user_by_username(session=session, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system",
        )

    # Convert UserRegister to UserCreate
    user_create = UserCreate(
        email=user_in.email,
        username=user_in.username,
        password=user_in.password,
        full_name=user_in.full_name,
    )

    user = user_service.create_user(session=session, user_create=user_create)
    return user


@router.get("/me", response_model=UserPrivate)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user's complete profile.
    """
    return current_user


@router.get("/me/stats", response_model=UserStats)
def read_user_stats(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get current user's statistics.
    """
    stats = user_service.get_user_stats(session=session, user_id=current_user.id)
    return UserStats(**stats)


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user profile.
    """
    # Check email uniqueness if email is being changed
    if user_in.email and user_in.email != current_user.email:
        existing_user = user_service.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    # Update user data
    user_data = user_in.model_dump(exclude_unset=True)
    updated_user = user_service.update_user(
        session=session, db_user=current_user, user_in=user_data
    )
    return updated_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    # Verify current password
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    # Check if new password is different
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one",
        )

    # Update password
    updated_user = user_service.update_user(
        session=session, db_user=current_user, user_in={"password": body.new_password}
    )

    return Message(message="Password updated successfully")


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user account.
    """
    # Prevent superusers from deleting themselves
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )

    # Delete user's content (cascade delete will handle relationships)
    # Additional cleanup can be added here if needed

    user_service.delete_user(session=session, user_id=current_user.id)
    return Message(message="User deleted successfully")


@router.get("/search", response_model=List[UserPublic])
def search_users(
    session: SessionDep,
    current_user: CurrentUser,
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """
    Search users by username, full_name, or email.
    """
    users = user_service.search_users(session=session, query=q, limit=limit)
    return users


@router.get("/verified", response_model=List[UserPublic])
def get_verified_users(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get all verified users (journalists, organizations, etc.).
    """
    users = user_service.get_verified_users(session=session, skip=skip, limit=limit)
    return users


@router.get("/journalists", response_model=List[UserPublic])
def get_journalists(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get all journalist users.
    """
    users = user_service.get_journalists(session=session, skip=skip, limit=limit)
    return users


@router.get("/{username}", response_model=UserProfilePublic)
def read_user_by_username(
    username: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by username.
    """
    user = user_service.get_user_by_username(session=session, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if user is private and current user doesn't follow them
    if user.is_private and user.id != current_user.id:
        # Check if current user follows this user
        is_following = user_service.is_following(
            session=session, follower_id=current_user.id, following_id=user.id
        )
        if not is_following:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="This account is private"
            )

    # Build profile with additional context
    profile = UserProfilePublic.model_validate(user)

    # Add following status from current user's perspective
    if current_user.id != user.id:
        profile.is_following = user_service.is_following(
            session=session, follower_id=current_user.id, following_id=user.id
        )
        # Calculate mutual followers (simplified)
        profile.mutual_followers_count = user_service.get_mutual_followers_count(
            session=session, user_id=current_user.id, other_user_id=user.id
        )

    return profile


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by ID.
    Requires admin privileges for other users.
    """
    if user_id == current_user.id:
        return current_user

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user (Superuser only).
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist in the system",
        )

    # Check email uniqueness
    if user_in.email and user_in.email != db_user.email:
        existing_user = user_service.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

    # Check username uniqueness
    if user_in.username and user_in.username != db_user.username:
        existing_user = user_service.get_user_by_username(
            session=session, username=user_in.username
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists",
            )

    db_user = user_service.update_user(
        session=session, db_user=db_user, user_in=user_in
    )
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user (Superuser only).
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user == current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )

    user_service.delete_user(session=session, user_id=user_id)
    return Message(message="User deleted successfully")


# Verification Routes
@router.post("/verification-request", response_model=Message)
def create_verification_request(
    *,
    session: SessionDep,
    verification_in: VerificationRequest,
    current_user: CurrentUser,
) -> Any:
    """
    Submit account verification request.
    """
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account is already verified",
        )

    # Create verification request (implementation depends on your verification system)
    # user_service.create_verification_request(session=session, user_id=current_user.id, request=verification_in)

    return Message(message="Verification request submitted successfully")


@router.get("/{username}/stats", response_model=UserStats)
def read_user_stats(
    username: str, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get user statistics by username.
    """
    user = user_service.get_user_by_username(session=session, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    stats = user_service.get_user_stats(session=session, user_id=user.id)
    return UserStats(**stats)
