"""OAuth client configurations for different providers."""

from typing import Dict, Any
from authlib.integrations.starlette_client import OAuth

from ..config import settings

# Initialize OAuth
oauth = OAuth()

# OAuth provider configurations
OAUTH_PROVIDERS = {
    "openrouter": {
        "name": "openrouter",
        "display_name": "OpenRouter",
        "client_id": settings.openrouter_client_id,
        "client_secret": settings.openrouter_client_secret,
        "authorization_endpoint": "https://openrouter.ai/oauth/authorize",
        "token_endpoint": "https://openrouter.ai/oauth/token",
        "userinfo_endpoint": "https://openrouter.ai/api/auth/me",
        "scopes": ["read:profile", "read:email"],
    },
    "google": {
        "name": "google",
        "display_name": "Google",
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
    "github": {
        "name": "github",
        "display_name": "GitHub",
        "client_id": settings.github_client_id,
        "client_secret": settings.github_client_secret,
        "authorization_endpoint": "https://github.com/login/oauth/authorize",
        "token_endpoint": "https://github.com/login/oauth/access_token",
        "userinfo_endpoint": "https://api.github.com/user",
        "scopes": ["user:email", "read:user"],
    },
}


def register_oauth_clients():
    """Register OAuth clients with authlib."""
    for provider_name, config in OAUTH_PROVIDERS.items():
        if config["client_id"] and config["client_secret"]:
            if provider_name == "google":
                # Google OAuth requires special configuration for OpenID Connect
                oauth.register(
                    name=provider_name,
                    client_id=config["client_id"],
                    client_secret=config["client_secret"],
                    access_token_url=config["token_endpoint"],
                    access_token_params=None,
                    authorize_url=config["authorization_endpoint"],
                    authorize_params=None,
                    api_base_url="https://www.googleapis.com/oauth2/v2/",
                    client_kwargs={"scope": "openid email profile"},
                    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
                )
            else:
                oauth.register(
                    name=provider_name,
                    client_id=config["client_id"],
                    client_secret=config["client_secret"],
                    authorize_url=config["authorization_endpoint"],
                    access_token_url=config["token_endpoint"],
                    client_kwargs={
                        "scope": " ".join(config["scopes"])
                    }
                )
    print("✅ OAuth clients registered")


def get_oauth_client(provider: str):
    """Get OAuth client for a specific provider."""
    return oauth.create_client(provider)


def get_provider_config(provider: str) -> Dict[str, Any]:
    """Get configuration for a specific OAuth provider."""
    return OAUTH_PROVIDERS.get(provider, {})
