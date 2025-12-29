#!/usr/bin/env python3
"""
Test Component API with provided JWT token
"""

import requests
import json
from typing import Optional

# Base URL
BASE_URL = "http://localhost:8000"

# JWT Token from user (Fresh token - expires at 2025-01-25 18:14:47 UTC)
JWT_TOKEN = "eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18zNUttWDBKTXBsbURzdmRJWkJFbk5VTU9BdUsiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwOi8vbG9jYWxob3N0OjMwMDAiLCJleHAiOjE3NjQwNzQ0ODcsImZ2YSI6WzEzMDAsLTFdLCJpYXQiOjE3NjQwNzQ0MjcsImlzcyI6Imh0dHBzOi8vYXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2IiwibmJmIjoxNzY0MDc0NDE3LCJvIjp7ImlkIjoib3JnXzM1am1kN0x2MzE3SHpFWkE2OEZlUVJ1azZPbCIsInJvbCI6ImFkbWluIiwic2xnIjoiY29kZW11cmYtMTc2MzYzMTkzOSJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsInNpZCI6InNlc3NfMzV2aE12SnZWMDVLRzRDcEhwVkUwRmxReEdSIiwic3RzIjoiYWN0aXZlIiwic3ViIjoidXNlcl8zNWptYUhiNEE0Z0lqRHRiYTlhWk5JdGVGbkYiLCJ2IjoyfQ.aQ7_U_L4yag0c92AMYakXLXmg8hZo-7O-mrCf-bVmiQALQYjcXLHc6fw3TXV3ftbypg77PTCX1Lyg290-_ZZxsemGXzD_CF13ziMHrzR34bRrXaItWXRQzWdORaDScdyOo6icCxnvMTCCtV96TjmxPjpW4IS833FinIV3iH_H8T0dKhP8N59GLPkR0XpR3ekkivwv2QAOkyyOmPxGw88hGSNjTlLtEMgU8Hb4BlV34FyLz0IdSwN6nS8rBFvnTk5bhJ20Utnh01yEJL4N_lNK-i0t1FgtbAGkuTf3j4M5mimaVpK3ZvB12kdjDE0N4fgxKcX9Ce1WnPl4PNWUUWoKw"


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")


def print_result(success: bool, message: str, details: Optional[str] = None):
    """Print test result"""
    color = Colors.GREEN if success else Colors.RED
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{color}{status}{Colors.RESET} {message}")
    if details:
        print(f"       {details}")


def test_get_all_components():
    """Test GET /api/components/"""
    print_header("TEST 1: Get All Components")
    
    url = f"{BASE_URL}/api/components/"
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Successfully fetched components")
            print(f"\nResponse Data:")
            print(f"  Total components: {len(data) if isinstance(data, list) else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"\nFirst component:")
                print(json.dumps(data[0], indent=2))
            else:
                print(f"\nFull response:")
                print(json.dumps(data, indent=2))
                
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_get_component_by_id(component_id: str):
    """Test GET /api/components/{id}"""
    print_header(f"TEST 2: Get Component by ID ({component_id})")
    
    url = f"{BASE_URL}/api/components/{component_id}"
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Successfully fetched component {component_id}")
            print(f"\nComponent Data:")
            print(json.dumps(data, indent=2))
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_create_component():
    """Test POST /api/components/"""
    print_header("TEST 3: Create New Component")
    
    url = f"{BASE_URL}/api/components/"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    component_data = {
        "title": "Test Component from API",
        "short_description": "A test component created via API with JWT token",
        "full_description": "This is a comprehensive test component created via API to verify JWT authentication and component creation functionality.",
        "category": "UI Components",
        "type": "Button",
        "language": "React",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "code": "export const TestComponent = () => { return <div>Test</div>; };",
        "tags": ["test", "api", "jwt"],
        "developer_name": "API Tester",
        "developer_experience": "5 years",
        "is_available_for_dev": True,
        "featured": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=component_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_result(True, "Successfully created component")
            print(f"\nCreated Component:")
            print(json.dumps(data, indent=2))
            
            # Extract component ID for further testing
            if 'component' in data and 'id' in data['component']:
                component_id = data['component']['id']
            elif 'id' in data:
                component_id = data['id']
            elif '_id' in data:
                component_id = data['_id']
            else:
                component_id = None
                
            if component_id:
                print(f"\n{Colors.YELLOW}Component ID: {component_id}{Colors.RESET}")
                return component_id
            else:
                print(f"\n{Colors.RED}Warning: Could not extract component ID from response{Colors.RESET}")
                return None
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_update_component(component_id: str):
    """Test PUT /api/components/{id}"""
    print_header(f"TEST 4: Update Component ({component_id})")
    
    url = f"{BASE_URL}/api/components/{component_id}"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "title": "Updated Test Component",
        "description": "This component has been updated via API"
    }
    
    try:
        response = requests.put(url, headers=headers, json=update_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Successfully updated component {component_id}")
            print(f"\nUpdated Component:")
            print(json.dumps(data, indent=2))
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_delete_component(component_id: str):
    """Test DELETE /api/components/{id}"""
    print_header(f"TEST 5: Delete Component ({component_id})")
    
    url = f"{BASE_URL}/api/components/{component_id}"
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    try:
        response = requests.delete(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print_result(True, f"Successfully deleted component {component_id}")
            try:
                data = response.json()
                print(f"\nResponse:")
                print(json.dumps(data, indent=2))
            except:
                print(f"\nNo response body (expected for DELETE)")
            return True
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return False
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return False


def test_get_my_components():
    """Test GET /api/components/my"""
    print_header("TEST 6: Get My Components")
    
    url = f"{BASE_URL}/api/components/my"
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Successfully fetched my components")
            print(f"\nMy Components:")
            print(f"  Total: {len(data) if isinstance(data, list) else 'N/A'}")
            
            if isinstance(data, list):
                for i, comp in enumerate(data[:3], 1):  # Show first 3
                    print(f"\n  Component {i}:")
                    print(f"    ID: {comp.get('id', comp.get('_id'))}")
                    print(f"    Title: {comp.get('title')}")
                    print(f"    Category: {comp.get('category')}")
            else:
                print(json.dumps(data, indent=2))
                
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def main():
    """Run all component API tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                      COMPONENT API TEST WITH JWT TOKEN                       ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Using JWT Token (first 50 chars): {JWT_TOKEN[:50]}...{Colors.RESET}\n")
    
    # Test 1: Get all components
    components = test_get_all_components()
    
    # Test 2: Get specific component (if any exist)
    if components and isinstance(components, list) and len(components) > 0:
        first_component_id = components[0].get('id') or components[0].get('_id')
        if first_component_id:
            test_get_component_by_id(str(first_component_id))
    
    # Test 3: Create a new component
    created_id = test_create_component()
    
    # Test 4 & 5: Update and delete the created component
    if created_id:
        test_update_component(str(created_id))
        
        # Verify the update worked
        test_get_component_by_id(str(created_id))
        
        # Clean up - delete the test component
        test_delete_component(str(created_id))
    
    # Test 6: Get my components
    test_get_my_components()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                            TESTS COMPLETED                                    ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")


if __name__ == "__main__":
    main()
