#!/usr/bin/env python3
"""
Test script to verify Component API endpoints
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def test_component_api():
    """Test the Component API endpoints"""
    
    print("🧪 Testing Component API Endpoints...")
    print("=" * 50)
    
    # Test data for creating a component
    test_component = {
        "title": "Test React Button",
        "category": "User Interface",
        "type": "React",
        "language": "TypeScript",
        "difficulty_level": "Easy",
        "plan_type": "Free",
        "pricing_inr": 0,
        "pricing_usd": 0,
        "short_description": "A reusable button component with multiple variants",
        "full_description": "This is a comprehensive button component built with React and TypeScript. It includes multiple variants, sizes, and states for maximum flexibility in your projects.",
        "preview_images": [],
        "git_repo_url": "https://github.com/test/react-button",
        "live_demo_url": "https://test-button-demo.vercel.app",
        "dependencies": ["react", "typescript", "tailwindcss"],
        "tags": ["button", "ui", "react", "component"],
        "developer_name": "Test Developer",
        "developer_experience": "5 years of React development",
        "is_available_for_dev": True,
        "featured": False,
        "code": "// Sample React Button Component\nexport const Button = ({ children, variant = 'primary' }) => {\n  return <button className={`btn btn-${variant}`}>{children}</button>;\n};",
        "readme_content": "# React Button Component\n\nA reusable button component for React applications.\n\n## Usage\n\n```jsx\nimport { Button } from './Button';\n\n<Button variant=\"primary\">Click me</Button>\n```"
    }
    
    # First, try to register a test user and login
    print("1. Testing user registration and login...")
    try:
        # Register test user
        register_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        register_response = requests.post(f"{API_BASE_URL}/auth/register", json=register_data)
        print(f"   Registration status: {register_response.status_code}")
        
        # Login to get token
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
        
        login_response = requests.post(f"{API_BASE_URL}/auth/login-json", json=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get("access_token")
            print(f"   ✅ Login successful, token received")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Auth error: {e}")
        return False
    
    # Set up headers with authorization
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test 2: Create a component
    print("\n2. Testing component creation...")
    try:
        create_response = requests.post(f"{API_BASE_URL}/components", json=test_component, headers=headers)
        print(f"   Create component status: {create_response.status_code}")
        
        if create_response.status_code == 200:
            created_component = create_response.json()
            component_id = created_component.get("id")
            print(f"   ✅ Component created successfully with ID: {component_id}")
        else:
            print(f"   ❌ Failed to create component: {create_response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Create component error: {e}")
        return False
    
    # Test 3: Get all components
    print("\n3. Testing get all components...")
    try:
        get_all_response = requests.get(f"{API_BASE_URL}/components", headers=headers)
        print(f"   Get all components status: {get_all_response.status_code}")
        
        if get_all_response.status_code == 200:
            all_components = get_all_response.json()
            component_count = len(all_components.get("components", []))
            print(f"   ✅ Retrieved {component_count} components")
        else:
            print(f"   ❌ Failed to get components: {get_all_response.text}")
    except Exception as e:
        print(f"   ❌ Get components error: {e}")
    
    # Test 4: Get specific component
    print("\n4. Testing get specific component...")
    try:
        get_one_response = requests.get(f"{API_BASE_URL}/components/{component_id}", headers=headers)
        print(f"   Get component status: {get_one_response.status_code}")
        
        if get_one_response.status_code == 200:
            component = get_one_response.json()
            print(f"   ✅ Retrieved component: {component.get('title')}")
        else:
            print(f"   ❌ Failed to get component: {get_one_response.text}")
    except Exception as e:
        print(f"   ❌ Get component error: {e}")
    
    # Test 5: Get user's components
    print("\n5. Testing get user's components...")
    try:
        user_components_response = requests.get(f"{API_BASE_URL}/components/user/my-components", headers=headers)
        print(f"   Get user components status: {user_components_response.status_code}")
        
        if user_components_response.status_code == 200:
            user_components = user_components_response.json()
            user_component_count = len(user_components.get("components", []))
            print(f"   ✅ User has {user_component_count} components")
        else:
            print(f"   ❌ Failed to get user components: {user_components_response.text}")
    except Exception as e:
        print(f"   ❌ Get user components error: {e}")
    
    # Test 6: Update component
    print("\n6. Testing component update...")
    try:
        update_data = {
            "title": "Updated Test React Button",
            "short_description": "An updated and improved button component"
        }
        
        update_response = requests.put(f"{API_BASE_URL}/components/{component_id}", json=update_data, headers=headers)
        print(f"   Update component status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            updated_component = update_response.json()
            print(f"   ✅ Component updated: {updated_component.get('title')}")
        else:
            print(f"   ❌ Failed to update component: {update_response.text}")
    except Exception as e:
        print(f"   ❌ Update component error: {e}")
    
    # Test 7: Delete component
    print("\n7. Testing component deletion...")
    try:
        delete_response = requests.delete(f"{API_BASE_URL}/components/{component_id}", headers=headers)
        print(f"   Delete component status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            print(f"   ✅ Component deleted successfully")
        else:
            print(f"   ❌ Failed to delete component: {delete_response.text}")
    except Exception as e:
        print(f"   ❌ Delete component error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Component API testing completed!")
    return True

if __name__ == "__main__":
    try:
        success = test_component_api()
        if success:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1)
