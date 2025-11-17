"""Clerk JWKS-based token verifier.

This verifier fetches the JWKS from the configured Clerk JWKS URL,
caches keys for a short TTL, verifies the token signature and
validates issuer/audience/expiry.
"""
import os
import time
from typing import Dict, Any, Optional

import requests
from jose import jwt, jwk
from jose.utils import base64url_decode
from fastapi import HTTPException, status

# Simple in-memory cache for JWKS
_JWKS_CACHE: Optional[Dict[str, Any]] = None
_JWKS_CACHE_EXPIRES_AT: float = 0.0
_JWKS_TTL = int(os.getenv("CLERK_JWKS_TTL", "300"))  # seconds

CLERK_ISSUER = os.getenv("CLERK_ISSUER", os.getenv("CLERK_ISSUER_URL", "https://api.clerk.com"))
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE")
JWKS_URL = os.getenv("CLERK_JWKS_URL", os.getenv("CLERK_JWKS", f"{CLERK_ISSUER}/.well-known/jwks.json"))
DEBUG_MODE = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")


def _fetch_jwks() -> Dict[str, Any]:
    global _JWKS_CACHE, _JWKS_CACHE_EXPIRES_AT
    now = time.time()
    if _JWKS_CACHE and now < _JWKS_CACHE_EXPIRES_AT:
        return _JWKS_CACHE

    try:
        resp = requests.get(JWKS_URL, timeout=5)
        resp.raise_for_status()
        jwks = resp.json()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unable to fetch JWKS: {e}")

    _JWKS_CACHE = jwks
    _JWKS_CACHE_EXPIRES_AT = now + _JWKS_TTL
    return jwks


def verify_clerk_token(token: str) -> Dict[str, Any]:
    """Verify a Clerk-issued JWT using JWKS and return its claims.

    Raises HTTPException on failure.
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        header = jwt.get_unverified_header(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")

    kid = header.get("kid")
    if not kid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing 'kid' header")

    jwks = _fetch_jwks()
    key = None
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            key = k
            break

    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to find matching JWK")

    # Verify signature manually using python-jose jwk
    try:
        public_key = jwk.construct(key)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to construct JWK public key")

    try:
        message, encoded_sig = token.rsplit('.', 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")

    try:
        decoded_sig = base64url_decode(encoded_sig.encode('utf-8'))
        verified = public_key.verify(message.encode('utf-8'), decoded_sig)
        if not verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature verification failed")

    # Get claims without re-checking signature (we already validated it)
    try:
        claims = jwt.get_unverified_claims(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to parse token claims")

    # Validate issuer
    if CLERK_ISSUER and claims.get("iss") and claims.get("iss") != CLERK_ISSUER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer")

    # Validate audience if provided. In debug mode, skip strict audience validation
    if CLERK_AUDIENCE and not DEBUG_MODE:
        aud = claims.get("aud")
        azp = claims.get("azp")
        # Accept the configured audience if it appears in `aud` or matches `azp`.
        if isinstance(aud, list):
            valid_aud = CLERK_AUDIENCE in aud or azp == CLERK_AUDIENCE
        else:
            valid_aud = (aud == CLERK_AUDIENCE) or (azp == CLERK_AUDIENCE)
        if not valid_aud:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token audience")

    # Validate expiry (with 60 second tolerance for clock skew)
    exp = claims.get("exp")
    if exp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing expiry")
    now = int(time.time())
    EXPIRY_TOLERANCE = 60  # Allow 60 seconds of tolerance
    if now > int(exp) + EXPIRY_TOLERANCE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

    return claims
