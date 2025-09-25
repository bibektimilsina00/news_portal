from typing import Any, Optional

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from starlette.config import Config

from app.core.config import settings
from app.modules.authentication.schema.auth import (
    OAuth2Callback,
    OAuth2Login,
    OAuth2Provider,
    UserLoginResponse,
)
from app.modules.authentication.services.oauth_service import oauth_service
from app.shared.deps.deps import SessionDep

router = APIRouter(prefix="/oauth", tags=["oauth"])

# OAuth configuration
config_data = {
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
    "FACEBOOK_CLIENT_ID": settings.FACEBOOK_CLIENT_ID,
    "FACEBOOK_CLIENT_SECRET": settings.FACEBOOK_CLIENT_SECRET,
    "TWITTER_CLIENT_ID": settings.TWITTER_CLIENT_ID,
    "TWITTER_CLIENT_SECRET": settings.TWITTER_CLIENT_SECRET,
    "GITHUB_CLIENT_ID": settings.GITHUB_CLIENT_ID,
    "GITHUB_CLIENT_SECRET": settings.GITHUB_CLIENT_SECRET,
}

config = Config(environ=config_data)
oauth = OAuth(config)

# Register OAuth providers
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="facebook",
    api_base_url="https://graph.facebook.com/",
    access_token_url="https://graph.facebook.com/oauth/access_token",
    authorize_url="https://www.facebook.com/dialog/oauth",
    client_kwargs={"scope": "email public_profile"},
)

oauth.register(
    name="twitter",
    api_base_url="https://api.twitter.com/",
    access_token_url="https://api.twitter.com/oauth/access_token",
    authorize_url="https://api.twitter.com/oauth/authenticate",
    client_kwargs={"scope": "email"},
)

oauth.register(
    name="github",
    api_base_url="https://api.github.com/",
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    client_kwargs={"scope": "user:email"},
)


@router.get("/{provider}/login")
async def oauth_login(provider: OAuth2Provider, request: Request) -> Any:
    """
    Initiate OAuth2 login flow
    """
    redirect_uri = f"{settings.API_BASE_URL}/auth/oauth/{provider}/callback"

    try:
        return await oauth.create_client(provider).authorize_redirect(
            request, redirect_uri
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate {provider} OAuth flow",
        )


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: OAuth2Provider, request: Request, session: SessionDep
) -> Any:
    """
    Handle OAuth2 callback
    """
    try:
        # Get access token from provider
        token = await oauth.create_client(provider).authorize_access_token(request)

        # Get user info from provider
        if provider == OAuth2Provider.GOOGLE:
            user_info = await oauth.google.parse_id_token(request, token)
        elif provider == OAuth2Provider.FACEBOOK:
            user_info = await oauth.facebook.get("me?fields=id,name,email", token=token)
            user_info = user_info.json()
        elif provider == OAuth2Provider.TWITTER:
            user_info = await oauth.twitter.get(
                "account/verify_credentials.json?include_email=true", token=token
            )
            user_info = user_info.json()
        elif provider == OAuth2Provider.GITHUB:
            user_info = await oauth.github.get("user", token=token)
            user_info = user_info.json()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider}",
            )

        # Process OAuth login
        login_response = await oauth_service.process_oauth_login(
            session=session, provider=provider, user_info=user_info, oauth_token=token
        )

        # Redirect to frontend with tokens
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={login_response.access_token}&refresh_token={login_response.refresh_token}"
        return RedirectResponse(url=redirect_url)

    except OAuthError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {error.error}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback processing failed",
        )


@router.post("/{provider}/token")
async def oauth_token_login(
    provider: OAuth2Provider, oauth_data: OAuth2Login, session: SessionDep
) -> Any:
    """
    OAuth2 token login (for mobile apps)
    """
    try:
        # Validate access token with provider
        user_info = await oauth_service.validate_oauth_token(
            provider=provider, access_token=oauth_data.access_token
        )

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OAuth access token",
            )

        # Process OAuth login
        login_response = await oauth_service.process_oauth_login(
            session=session,
            provider=provider,
            user_info=user_info,
            oauth_token={"access_token": oauth_data.access_token},
        )

        return login_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth token validation failed",
        )


@router.get("/{provider}/unlink")
async def unlink_oauth_provider(
    provider: OAuth2Provider,
    session: SessionDep,
    current_user: CurrentUser = Depends(get_current_active_user),
) -> Any:
    """
    Unlink OAuth provider from user account
    """
    success = await oauth_service.unlink_oauth_provider(
        session=session, user_id=current_user.id, provider=provider
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to unlink {provider} account",
        )

    return {"message": f"{provider} account unlinked successfully"}


@router.get("/providers")
async def get_oauth_providers() -> Any:
    """
    Get available OAuth providers
    """
    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "icon": "google",
                "enabled": bool(settings.GOOGLE_CLIENT_ID),
            },
            {
                "name": "facebook",
                "display_name": "Facebook",
                "icon": "facebook",
                "enabled": bool(settings.FACEBOOK_CLIENT_ID),
            },
            {
                "name": "twitter",
                "display_name": "Twitter",
                "icon": "twitter",
                "enabled": bool(settings.TWITTER_CLIENT_ID),
            },
            {
                "name": "github",
                "display_name": "GitHub",
                "icon": "github",
                "enabled": bool(settings.GITHUB_CLIENT_ID),
            },
        ]
    }
