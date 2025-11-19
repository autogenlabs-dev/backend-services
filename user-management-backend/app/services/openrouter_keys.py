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
