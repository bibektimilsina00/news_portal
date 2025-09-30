import uuid

from fastapi import APIRouter, HTTPException, Query

from app.modules.posts.schema.post import (
    PostCreate,
    PostListResponse,
    PostResponse,
    PostUpdate,
)
from app.modules.posts.services.post_service import post_service
from app.shared.deps.deps import CurrentUser, SessionDep

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse)
def create_post(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    post_data: PostCreate,
):
    """Create a new post"""
    try:
        post = post_service.create_post(session=session, post_create=post_data)
        return PostResponse.model_validate(post)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=PostListResponse)
def get_posts(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Get published posts"""
    try:
        posts = post_service.get_published_posts(
            session=session, skip=skip, limit=limit
        )

        return PostListResponse(
            posts=[PostResponse.model_validate(post) for post in posts],
            total=len(posts),
            page=skip // limit + 1,
            per_page=limit,
            has_next=len(posts) == limit,
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/feed", response_model=PostListResponse)
def get_feed(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Get personalized feed for current user"""
    try:
        # For now, just return published posts (we'll implement proper feed later)
        posts = post_service.get_published_posts(
            session=session, skip=skip, limit=limit
        )

        return PostListResponse(
            posts=[PostResponse.model_validate(post) for post in posts],
            total=len(posts),
            page=skip // limit + 1,
            per_page=limit,
            has_next=len(posts) == limit,
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    post_id: uuid.UUID,
):
    """Get a specific post by ID"""
    try:
        post = post_service.get_post(session=session, post_id=post_id)
        return PostResponse.model_validate(post)
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    post_id: uuid.UUID,
    post_data: PostUpdate,
):
    """Update a post"""
    try:
        post = post_service.update_post(
            session=session, post_id=post_id, user_id=current_user.id, post_in=post_data
        )
        return PostResponse.model_validate(post)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{post_id}")
def delete_post(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    post_id: uuid.UUID,
):
    """Delete a post"""
    try:
        success = post_service.delete_post(
            session=session, post_id=post_id, user_id=current_user.id
        )
        return {"message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/publish")
def publish_post(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    post_id: uuid.UUID,
):
    """Publish a draft post"""
    try:
        post = post_service.publish_post(
            session=session, post_id=post_id, user_id=current_user.id
        )
        return {"message": "Post published successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/pin")
def pin_post(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    post_id: uuid.UUID,
):
    """Pin a post"""
    try:
        post = post_service.pin_post(
            session=session, post_id=post_id, user_id=current_user.id
        )
        return {"message": "Post pinned successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{post_id}/unpin")
def unpin_post(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    post_id: uuid.UUID,
):
    """Unpin a post"""
    try:
        post = post_service.unpin_post(
            session=session, post_id=post_id, user_id=current_user.id
        )
        return {"message": "Post unpinned successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=PostListResponse)
def get_user_posts(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Get posts by a specific user"""
    try:
        posts = post_service.get_posts_by_user(
            session=session, user_id=user_id, skip=skip, limit=limit
        )

        return PostListResponse(
            posts=[PostResponse.model_validate(post) for post in posts],
            total=len(posts),
            page=skip // limit + 1,
            per_page=limit,
            has_next=len(posts) == limit,
            has_prev=skip > 0,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
