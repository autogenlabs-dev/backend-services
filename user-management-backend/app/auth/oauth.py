"""OAuth client configurations for different providers."""

from typing import Dict, Any
from authlib.integrations.starlette_client import OAuth

from ..config import settings

# Initialize OAuth
oauth = OAuth()

# OAuth provider configurations
OAUTH_PROVIDERS = {    "openrouter": {
        "name": "openrouter",
        "display_name": "OpenRouter",
        "client_id": settings.openrouter_client_id,
        "client_secret": settings.openrouter_client_secret,
        "authorization_endpoint": "https://openrouter.ai/oauth/authorize",
        "token_endpoint": "https://openrouter.ai/oauth/token",
        "userinfo_endpoint": "https://openrouter.ai/api/auth/me",
        "scopes": ["read:profile", "read:email"],
    },
    "glama": {
        "name": "glama",
        "display_name": "Glama",
        "client_id": settings.glama_client_id,
        "client_secret": settings.glama_client_secret,
        "authorization_endpoint": "https://api.glama.ai/oauth/authorize",
        "token_endpoint": "https://api.glama.ai/oauth/token",
        "userinfo_endpoint": "https://api.glama.ai/oauth/userinfo",
        "scopes": ["openid", "profile", "email"],    },
    "requesty": {
        "name": "requesty",
        "display_name": "Requesty",
        "client_id": settings.requesty_client_id,
        "client_secret": settings.requesty_client_secret,
        "authorization_endpoint": "https://requesty.io/oauth/authorize",
        "token_endpoint": "https://requesty.io/oauth/token",
        "userinfo_endpoint": "https://requesty.io/api/user",
        "scopes": ["user:read"],
    },
    "aiml": {
        "name": "aiml",
        "display_name": "AIML",
        "client_id": settings.aiml_client_id,
        "client_secret": settings.aiml_client_secret,
        "authorization_endpoint": "https://api.aimlapi.com/oauth/authorize",
        "token_endpoint": "https://api.aimlapi.com/oauth/token",
        "userinfo_endpoint": "https://api.aimlapi.com/user",
        "scopes": ["read:profile", "read:email"],
    },
}


def register_oauth_clients():
    """Register OAuth clients with authlib."""
    for provider_name, config in OAUTH_PROVIDERS.items():
        if config["client_id"] and config["client_secret"]:
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


def get_oauth_client(provider: str):
    """Get OAuth client for a specific provider."""
    return oauth.create_client(provider)


def get_provider_config(provider: str) -> Dict[str, Any]:
    """Get configuration for a specific OAuth provider."""
    return OAUTH_PROVIDERS.get(provider, {})
