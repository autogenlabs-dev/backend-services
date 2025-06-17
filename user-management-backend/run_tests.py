#!/usr/bin/env python3
"""
Quick Test Runner for User Management Backend

This script runs the essential tests to verify the backend is working correctly.
"""

import subprocess
import sys
import os

def run_test(test_path, description):
    """Run a test and return success status."""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, test_path], 
                              capture_output=True, text=True, cwd=os.path.dirname(test_path))
        
        if result.returncode == 0:
            print("✅ PASSED")
            return True
        else:
            print("❌ FAILED")
            if result.stdout:
                print("STDOUT:", result.stdout[-200:])  # Last 200 chars
            if result.stderr:
                print("STDERR:", result.stderr[-200:])  # Last 200 chars
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all essential tests."""
    print("🚀 User Management Backend - Quick Test Suite")
    print("=" * 60)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "tests")
    
    tests = [
        (os.path.join(base_dir, "integration", "test_full_flow_comprehensive.py"), 
         "Comprehensive Integration Test"),
        (os.path.join(base_dir, "api", "test_api_key_auth.py"), 
         "API Key Authentication Test"),
        (os.path.join(base_dir, "stripe", "test_stripe_comprehensive.py"), 
         "Stripe Payment Integration Test"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_path, description in tests:
        if os.path.exists(test_path):
            if run_test(test_path, description):
                passed += 1
        else:
            print(f"\n⚠️ {description}")
            print("=" * 50)
            print(f"❌ Test file not found: {test_path}")
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is ready for production.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
