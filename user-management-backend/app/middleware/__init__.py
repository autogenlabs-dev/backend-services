"""
Middleware package for FastAPI marketplace backend.
"""

from .rate_limiting import (
    rate_limit_middleware,
    apply_rate_limit,
    add_rate_limit_headers,
)

from .auth import (
    get_current_user_from_token,
    require_auth,
    require_role,
    require_admin,
    require_creator_or_admin,
    require_developer,
    require_user,
    check_content_ownership,
    check_content_access,
    RoleChecker,
    AdminOnly,
    AnyUser,
)

# Backwards-compatible alias: some modules still import DeveloperOrAdmin
DeveloperOrAdmin = require_creator_or_admin

__all__ = [
    "rate_limit_middleware",
    "apply_rate_limit",
    "add_rate_limit_headers",
    "get_current_user_from_token",
    "require_auth",
    "require_role",
    "require_admin",
    "require_creator_or_admin",
    "require_developer",
    "require_user",
    "check_content_ownership",
    "check_content_access",
    "RoleChecker",
    "AdminOnly",
    "DeveloperOrAdmin",
    "AnyUser",
]
