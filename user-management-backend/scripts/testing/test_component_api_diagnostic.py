#!/usr/bin/env python3
"""
Diagnostic test for Component API to identify the "Component Not Found" error.
This script tests the full lifecycle: create component → get component by ID
"""

import requests
import json
from typing import Dict, Any
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on a different port
API_BASE = f"{BASE_URL}/api"

# Test credentials - you'll need to provide valid auth token
# You can get this from your browser's developer tools after logging in
AUTH_TOKEN = None  # Set this to your actual JWT token

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_emoji_log(emoji: str, message: str, data: Any = None):
    """Print emoji-prefixed log like the frontend"""
    print(f"{emoji} {message}")
    if data:
        print(json.dumps(data, indent=2))

def test_component_lifecycle():
    """Test the complete component creation and retrieval flow"""
    
    print_section("COMPONENT API DIAGNOSTIC TEST")
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json"
    }
    
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    else:
        print("⚠️  WARNING: No AUTH_TOKEN provided. Request will likely fail.")
        print("   Please set AUTH_TOKEN in the script or pass it as an environment variable.")
        print("   You can get the token from browser DevTools → Application → Cookies")
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(0)
    
    # Step 1: Create a test component
    print_section("STEP 1: CREATE COMPONENT")
    
    test_component_data = {
        "title": "Diagnostic Test Component",
        "category": "UI Elements",
        "type": "Button",
        "language": "React",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "pricing_inr": 0,
        "pricing_usd": 0,
        "short_description": "Test component for diagnostic purposes",
        "full_description": "This is a test component created by the diagnostic script",
        "preview_images": [],
        "dependencies": ["react", "react-dom"],
        "tags": ["test", "diagnostic"],
        "developer_name": "System Test",
        "developer_experience": "Testing",
        "is_available_for_dev": True,
        "featured": False
    }
    
    print_emoji_log("🔵", "Creating component with data:", test_component_data)
    
    try:
        response = requests.post(
            f"{API_BASE}/components/",
            headers=headers,
            json=test_component_data,
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print_emoji_log("🟢", "Component created successfully. Raw response:", response_data)
            
            # Check for ID in different possible locations
            component_id = None
            
            # Check in component object
            if "component" in response_data:
                component = response_data["component"]
                print_emoji_log("🔍", "Inspecting component object keys:", list(component.keys()))
                
                # Check for 'id' field
                if "id" in component:
                    component_id = component["id"]
                    print_emoji_log("🔑", f"Component ID from response.component.id: {component_id}")
                elif "_id" in component:
                    component_id = component["_id"]
                    print_emoji_log("🔑", f"Component ID from response.component._id: {component_id}")
                else:
                    print_emoji_log("❌", "ERROR: No 'id' or '_id' field found in component object!")
                    print_emoji_log("🔍", "Available fields:", component.keys())
            else:
                print_emoji_log("❌", "ERROR: No 'component' field in response!")
            
            # Check for direct ID field
            if "id" in response_data:
                print_emoji_log("🔑", f"Component ID from response.id: {response_data['id']}")
                if not component_id:
                    component_id = response_data["id"]
            
            if not component_id:
                print_emoji_log("❌", "CRITICAL: Could not extract component ID from response!")
                print_emoji_log("🔍", "Full response structure:", response_data)
                return False
            
            # Validate ID format
            print_emoji_log("🔄", f"Validating component ID: {component_id}")
            print_emoji_log("✅", f"ID Type: {type(component_id)}")
            print_emoji_log("✅", f"ID Length: {len(str(component_id))}")
            
            # Step 2: Fetch the component by ID
            print_section("STEP 2: FETCH COMPONENT BY ID")
            
            fetch_url = f"{API_BASE}/components/{component_id}"
            print_emoji_log("🔗", f"Fetching from URL: {fetch_url}")
            
            fetch_response = requests.get(
                fetch_url,
                headers=headers,
                timeout=10
            )
            
            print(f"\n📊 Fetch Response Status: {fetch_response.status_code}")
            
            if fetch_response.status_code == 200:
                fetch_data = fetch_response.json()
                print_emoji_log("✅", "Component fetched successfully:", fetch_data)
                
                # Verify IDs match
                if "component" in fetch_data:
                    fetched_id = fetch_data["component"].get("id") or fetch_data["component"].get("_id")
                    if fetched_id == component_id:
                        print_emoji_log("✅", "SUCCESS: IDs match! Component lifecycle works correctly.")
                        return True
                    else:
                        print_emoji_log("❌", f"ERROR: ID mismatch! Created: {component_id}, Fetched: {fetched_id}")
                        return False
                else:
                    print_emoji_log("❌", "ERROR: No component in fetch response")
                    return False
            else:
                error_data = fetch_response.json() if fetch_response.headers.get("content-type") == "application/json" else fetch_response.text
                print_emoji_log("❌", f"ERROR: Failed to fetch component (Status {fetch_response.status_code})", error_data)
                return False
                
        else:
            error_data = response.json() if response.headers.get("content-type") == "application/json" else response.text
            print_emoji_log("❌", f"ERROR: Failed to create component (Status {response.status_code})", error_data)
            return False
            
    except requests.exceptions.ConnectionError:
        print_emoji_log("❌", "ERROR: Cannot connect to backend. Is the server running?")
        print(f"   Tried connecting to: {BASE_URL}")
        return False
    except Exception as e:
        print_emoji_log("❌", f"ERROR: Unexpected exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    print("\n🚀 Starting Component API Diagnostic Test")
    print(f"📍 Backend URL: {BASE_URL}")
    
    # Check if we can reach the backend
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Backend is reachable (Status: {health_response.status_code})")
    except:
        print("⚠️  Warning: Could not reach backend health endpoint")
    
    # Run the test
    success = test_component_lifecycle()
    
    print_section("TEST RESULTS")
    if success:
        print("✅ All tests passed! Component API is working correctly.")
        print("   If you're still experiencing issues, the problem is likely in the frontend.")
    else:
        print("❌ Tests failed! There is an issue with the backend API.")
        print("   Review the logs above to identify the problem.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
