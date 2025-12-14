"""Utilities for managing per-user OpenRouter API keys via the provisioning API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional, Tuple

import httpx

from ..config import settings
from ..models.user import User

logger = logging.getLogger(__name__)

OPENROUTER_KEYS_ENDPOINT = f"{settings.openrouter_api_base.rstrip('/')}/keys"


def _extract_key_payload(data: dict) -> Tuple[str, Optional[str]]:
    """Extract the key value and hash from OpenRouter responses."""
    if not isinstance(data, dict):
        raise ValueError("Invalid OpenRouter response structure")

    if "key" in data and data.get("key"):
        return data["key"], data.get("hash")

    inner = data.get("data")
    if isinstance(inner, dict):
        if "key" in inner and inner.get("key"):
            return inner["key"], inner.get("hash")
    elif isinstance(inner, list) and inner:
        first = inner[0]
        if isinstance(first, dict) and first.get("key"):
            return first["key"], first.get("hash")

    raise ValueError("OpenRouter response did not include a key value")


async def _request_openrouter_key(user: User, limit: Optional[int] = None) -> Tuple[str, Optional[str]]:
    provisioning_key = settings.openrouter_provisioning_api_key
    if not provisioning_key:
        raise RuntimeError("OPENROUTER_PROVISIONING_API_KEY is not configured")

    payload = {
        "name": f"codemurf-user-{user.id}",
        "label": user.email,
    }
    if limit is not None:
        payload["limit"] = limit

    headers = {
        "Authorization": f"Bearer {provisioning_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENROUTER_KEYS_ENDPOINT, headers=headers, json=payload)
    if response.status_code >= 400:
        logger.error("OpenRouter key provisioning failed: %s", response.text)
        response.raise_for_status()

    key_value, key_hash = _extract_key_payload(response.json())
    return key_value, key_hash


async def ensure_user_openrouter_key(user: User) -> Optional[str]:
    """Ensure the user has an OpenRouter API key, provisioning one if necessary."""
    if getattr(user, "openrouter_api_key", None):
        return user.openrouter_api_key

    try:
        key_value, key_hash = await _request_openrouter_key(user)
    except Exception as exc:  # noqa: BLE001 - we log and bubble up
        logger.exception("Failed to provision OpenRouter key for user %s", user.id)
        raise exc

    user.openrouter_api_key = key_value
    user.openrouter_api_key_hash = key_hash
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    return key_value


async def refresh_user_openrouter_key(user: User) -> str:
    """Always create a brand new OpenRouter key for the user."""
    key_value, key_hash = await _request_openrouter_key(user)
    user.openrouter_api_key = key_value
    user.openrouter_api_key_hash = key_hash
    user.updated_at = datetime.now(timezone.utc)
    await user.save()
    return key_value


async def provision_openrouter_key_with_limit(user: User, limit_usd: float = 10.0) -> str:
    """
    Provision an OpenRouter key with a spending limit for PAYG users.
    
    Args:
        user: The user to provision the key for
        limit_usd: Spending limit in USD (default $10 for PAYG)
    
    Returns:
        The provisioned API key
    """
    try:
        # Convert USD to cents (OpenRouter uses cents for limits)
        limit_cents = int(limit_usd * 100)
        key_value, key_hash = await _request_openrouter_key(user, limit=limit_cents)
        
        user.openrouter_api_key = key_value
        user.openrouter_api_key_hash = key_hash
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
        
        logger.info(f"Provisioned OpenRouter key with ${limit_usd} limit for user {user.id}")
        return key_value
        
    except Exception as exc:
        logger.exception(f"Failed to provision limited OpenRouter key for user {user.id}")
        raise exc


async def get_openrouter_credits(user: User) -> Optional[dict]:
    """
    Get remaining credits/usage for a user's OpenRouter key.
    
    Returns dict with:
        - limit: Total spending limit in USD
        - usage: Amount used in USD
        - remaining: Remaining credits in USD
        - is_free_tier: Whether user is on free tier (based on subscription)
    """
    # Determine if user is on free tier based on subscription
    subscription = getattr(user, 'subscription', None)
    subscription_value = subscription.value if hasattr(subscription, 'value') else str(subscription) if subscription else 'free'
    is_paid_subscription = subscription_value.lower() in ('pro', 'ultra', 'payg')
    
    if not user.openrouter_api_key:
        return {
            "is_free_tier": not is_paid_subscription,
            "subscription": subscription_value,
            "limit_usd": None,
            "usage_usd": 0,
            "remaining_usd": None
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.openrouter_api_base.rstrip('/')}/auth/key",
                headers={"Authorization": f"Bearer {user.openrouter_api_key}"}
            )
        
        if response.status_code >= 400:
            logger.warning(f"Failed to get credits for user {user.id}: {response.text}")
            return {
                "is_free_tier": not is_paid_subscription,
                "subscription": subscription_value,
                "limit_usd": None,
                "usage_usd": 0,
                "remaining_usd": None
            }
        
        data = response.json()
        
        # Extract relevant fields from OpenRouter response
        # The response structure may vary - handle gracefully
        key_data = data.get("data", data)
        
        limit = key_data.get("limit")  # In cents
        usage = key_data.get("usage", 0)  # In cents
        
        result = {
            # is_free_tier should be based on subscription, not just OpenRouter limit
            "is_free_tier": not is_paid_subscription,
            "subscription": subscription_value,
            "limit_usd": limit / 100 if limit else None,
            "usage_usd": usage / 100 if usage else 0,
            "remaining_usd": (limit - usage) / 100 if limit else None
        }
        
        return result
        
    except Exception as exc:
        logger.exception(f"Failed to get OpenRouter credits for user {user.id}")
        return {
            "is_free_tier": not is_paid_subscription,
            "subscription": subscription_value,
            "limit_usd": None,
            "usage_usd": 0,
            "remaining_usd": None
        }



async def add_openrouter_credits(user: User, additional_usd: float) -> Optional[str]:
    """
    Add credits to a user's OpenRouter key by updating the limit.
    For PAYG users who want to top up.
    
    Note: This creates a new key with the updated limit.
    """
    try:
        # Get current usage
        current = await get_openrouter_credits(user)
        current_limit = current.get("limit_usd", 0) if current else 0
        
        # Calculate new limit
        new_limit = current_limit + additional_usd
        
        # Provision new key with updated limit
        return await provision_openrouter_key_with_limit(user, limit_usd=new_limit)
        
    except Exception as exc:
        logger.exception(f"Failed to add credits for user {user.id}")
        raise exc

