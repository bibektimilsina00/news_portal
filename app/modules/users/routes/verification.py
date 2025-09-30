import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.modules.users.schema.verification import (
    PublicVerificationInfo,
    VerificationAppealRequest,
    VerificationBadgeResponse,
    VerificationBadgesList,
    VerificationRequestCreate,
    VerificationRequestResponse,
    VerificationRequestsList,
    VerificationReviewRequest,
)
from app.modules.users.services.verification_service import verification_service
from app.shared.deps.deps import CurrentUser, SessionDep, get_current_active_superuser

router = APIRouter(prefix="/verification", tags=["verification"])


@router.post("/request", response_model=VerificationRequestResponse)
def create_verification_request(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    request_data: VerificationRequestCreate,
):
    """Create a new verification request"""
    try:
        request = verification_service.create_verification_request(
            session=session, user_id=current_user.id, request_data=request_data
        )
        return VerificationRequestResponse.model_validate(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/request", response_model=VerificationRequestResponse)
def get_my_verification_request(
    *,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get current user's verification request"""
    request = verification_service.get_user_verification_request(
        session=session, user_id=current_user.id
    )
    if not request:
        raise HTTPException(status_code=404, detail="No verification request found")
    return VerificationRequestResponse.model_validate(request)


@router.get("/badge", response_model=VerificationBadgeResponse)
def get_my_verification_badge(
    *,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get current user's active verification badge"""
    badge = verification_service.get_user_verification_badge(
        session=session, user_id=current_user.id
    )
    if not badge:
        raise HTTPException(
            status_code=404, detail="No active verification badge found"
        )
    return VerificationBadgeResponse.model_validate(badge)


@router.get("/history", response_model=VerificationBadgesList)
def get_my_verification_history(
    *,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Get current user's verification history"""
    badges = verification_service.get_user_verification_history(
        session=session, user_id=current_user.id
    )
    return VerificationBadgesList(
        badges=[VerificationBadgeResponse.model_validate(badge) for badge in badges],
        total=len(badges),
    )


@router.post("/appeal", response_model=VerificationRequestResponse)
def appeal_verification_rejection(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    appeal_data: VerificationAppealRequest,
):
    """Appeal a rejected verification request"""
    try:
        request = verification_service.appeal_verification_rejection(
            session=session, user_id=current_user.id, appeal_data=appeal_data
        )
        return VerificationRequestResponse.model_validate(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/public/{user_id}", response_model=PublicVerificationInfo)
def get_user_verification_info(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
):
    """Get public verification information for a user"""
    badge = verification_service.get_user_verification_badge(
        session=session, user_id=user_id
    )

    if badge:
        return PublicVerificationInfo(
            is_verified=True,
            verification_type=badge.badge_type,
            badge_name=badge.badge_name,
            verified_since=badge.issued_at,
            badge_expires_at=badge.expires_at,
        )
    else:
        return PublicVerificationInfo(is_verified=False)


# Admin routes
@router.get(
    "/admin/requests",
    response_model=VerificationRequestsList,
    dependencies=[Depends(get_current_active_superuser)],
)
def get_pending_verification_requests(
    *,
    session: SessionDep,
    skip: int = 0,
    limit: int = 50,
):
    """Get all pending verification requests (admin only)"""
    requests = verification_service.get_pending_requests(
        session=session, skip=skip, limit=limit
    )

    return VerificationRequestsList(
        requests=[VerificationRequestResponse.model_validate(req) for req in requests],
        total=len(requests),
        page=skip // limit + 1,
        per_page=limit,
        has_next=len(requests) == limit,
        has_prev=skip > 0,
    )


@router.post(
    "/admin/review/{request_id}",
    response_model=VerificationRequestResponse,
    dependencies=[Depends(get_current_active_superuser)],
)
def review_verification_request(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    request_id: uuid.UUID,
    review_data: VerificationReviewRequest,
):
    """Review a verification request (admin only)"""
    request = verification_service.review_verification_request(
        session=session,
        request_id=request_id,
        reviewer_id=current_user.id,
        review_data=review_data,
    )

    if not request:
        raise HTTPException(status_code=404, detail="Verification request not found")

    return VerificationRequestResponse.model_validate(request)


@router.post(
    "/admin/mark-review/{request_id}",
    response_model=VerificationRequestResponse,
    dependencies=[Depends(get_current_active_superuser)],
)
def mark_request_under_review(
    *,
    session: SessionDep,
    request_id: uuid.UUID,
):
    """Mark a verification request as under review (admin only)"""
    request = verification_service.mark_request_under_review(
        session=session, request_id=request_id
    )

    if not request:
        raise HTTPException(status_code=404, detail="Verification request not found")

    return VerificationRequestResponse.model_validate(request)
