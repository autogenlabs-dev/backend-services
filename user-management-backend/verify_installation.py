#!/usr/bin/env python3
"""Installation verification script for Autogen Backend."""

import requests
import json
import sys
import time
from pathlib import Path

def test_server_health():
    """Test if the server is running and healthy."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server Health Check: PASSED")
            print(f"   Status: {data.get('status')}")
            print(f"   App: {data.get('app')}")
            return True
        else:
            print(f"❌ Server Health Check: FAILED (Status: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"❌ Server Health Check: FAILED (Error: {e})")
        return False

def test_oauth_providers():
    """Test OAuth providers endpoint."""
    try:
        response = requests.get("http://localhost:8000/auth/providers", timeout=5)
        if response.status_code == 200:
            data = response.json()
            providers = data.get('providers', [])
            print("✅ OAuth Providers: PASSED")
            print(f"   Found {len(providers)} providers:")
            for provider in providers:
                print(f"   - {provider['display_name']} ({provider['name']})")
            return True
        else:
            print(f"❌ OAuth Providers: FAILED (Status: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"❌ OAuth Providers: FAILED (Error: {e})")
        return False

def test_api_documentation():
    """Test API documentation accessibility."""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API Documentation: ACCESSIBLE")
            print("   Available at: http://localhost:8000/docs")
            return True
        else:
            print(f"❌ API Documentation: FAILED (Status: {response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"❌ API Documentation: FAILED (Error: {e})")
        return False

def test_database_files():
    """Check if database files exist."""
    db_file = Path("test.db")
    if db_file.exists():
        print("✅ Database File: EXISTS")
        print(f"   Location: {db_file.absolute()}")
        return True
    else:
        print("❌ Database File: NOT FOUND")
        return False

def test_environment_config():
    """Check if environment configuration exists."""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Environment Config: EXISTS")
        print(f"   Location: {env_file.absolute()}")
        return True
    else:
        print("❌ Environment Config: NOT FOUND")
        return False

def main():
    """Run all verification tests."""
    print("🔍 Autogen Backend Installation Verification")
    print("=" * 50)
    
    tests = [
        ("Server Health", test_server_health),
        ("Environment Config", test_environment_config),
        ("Database Files", test_database_files),
        ("OAuth Providers", test_oauth_providers),
        ("API Documentation", test_api_documentation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(0.5)  # Small delay for readability
    
    print("\n" + "=" * 50)
    print(f"📊 VERIFICATION SUMMARY")
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 INSTALLATION VERIFICATION: SUCCESSFUL!")
        print("\nYour Autogen Backend is fully operational!")
        print("\nNext Steps:")
        print("- Access API documentation: http://localhost:8000/docs")
        print("- Replace development keys with production keys in .env")
        print("- Test VS Code extension integration")
        print("- Set up Redis for production rate limiting (optional)")
        return 0
    else:
        print("⚠️  INSTALLATION VERIFICATION: INCOMPLETE")
        print(f"\n{total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
