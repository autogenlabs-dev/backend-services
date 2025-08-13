#!/usr/bin/env python3
"""
Quick test to verify component creation through API
"""
import asyncio
import json
import requests
import sys
import os

def test_component_creation():
    """Test component creation via API"""
    print("🧪 Testing Component Creation API")
    print("=" * 50)
    
    # Test data for component creation
    component_data = {
        "title": "Test Card Component",
        "category": "Layout", 
        "type": "card",
        "language": "HTML/CSS",
        "difficulty_level": "Intermediate",
        "plan_type": "Premium",
        "pricing_inr": 500,
        "pricing_usd": 6,
        "short_description": "A test card component",
        "full_description": "This is a test card component for testing purposes",
        "dependencies": ["React"],
        "tags": ["card", "layout"],
        "developer_name": "Test Developer",
        "developer_experience": "Senior",
        "is_available_for_dev": True,
        "featured": False,
        "code": '{"html": "<div class=\\"card\\">Test</div>", "css": ".card { background: white; }"}',
        "readme_content": "# Test Component\\nThis is a test component"
    }
    
    # You would need a valid JWT token here
    # For testing, you can get one by logging in through the API first
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
    }
    
    try:
        # Test the component creation endpoint
        response = requests.post(
            "http://localhost:8000/components/",
            headers=headers,
            json=component_data
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Authentication required - Need valid JWT token")
            print("💡 To fix the frontend 401 error:")
            print("   1. Check if user is logged in properly")
            print("   2. Verify JWT token is being sent in Authorization header")
            print("   3. Check token expiration")
        elif response.status_code == 200:
            print("✅ Component creation successful!")
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Test completed!")

if __name__ == "__main__":
    test_component_creation()
