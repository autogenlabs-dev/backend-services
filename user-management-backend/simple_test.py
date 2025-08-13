#!/usr/bin/env python3
"""Simple test script to check basic functionality."""

print("🔍 Testing basic imports...")

try:
    print("Testing audit log import...")
    from app.models.audit_log import AuditLog, ActionType, AuditSeverity
    print("✅ Audit Log model imported successfully")
except Exception as e:
    print(f"❌ Audit Log model error: {e}")

try:
    print("Testing email service import...")
    from app.utils.email_service import email_service
    print("✅ Email service imported successfully")
except Exception as e:
    print(f"❌ Email service error: {e}")

print("✅ Basic import tests completed!")