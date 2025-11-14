#!/usr/bin/env python3
"""Test script to check CORS configuration"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

print("=== CORS Configuration Test ===")
print(f"Environment: {getattr(settings, 'environment', 'development')}")
print(f"CORS Origins: {settings.backend_cors_origins}")
print(f"Type of CORS Origins: {type(settings.backend_cors_origins)}")

# Check if production URLs are in the list
production_urls = ["https://codemurf.com", "https://www.codemurf.com"]
for url in production_urls:
    if url in settings.backend_cors_origins:
        print(f"✅ {url} is allowed")
    else:
        print(f"❌ {url} is NOT allowed")

# Check for duplicates
if len(settings.backend_cors_origins) != len(set(settings.backend_cors_origins)):
    print("⚠️  Duplicate CORS origins detected!")
    duplicates = [x for x in settings.backend_cors_origins if settings.backend_cors_origins.count(x) > 1]
    print(f"Duplicates: {set(duplicates)}")
else:
    print("✅ No duplicate CORS origins")