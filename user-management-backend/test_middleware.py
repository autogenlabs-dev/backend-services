#!/usr/bin/env python3
"""Test middleware imports."""

print("🔍 Testing middleware imports...")

try:
    print("Testing middleware import...")
    from app.middleware.auth import require_admin, require_role, get_current_user_from_token
    print("✅ Authentication middleware imported successfully")
except Exception as e:
    print(f"❌ Middleware error: {e}")

print("✅ Middleware import test completed!")