#!/usr/bin/env python3
"""
Test Template API with JWT token
Comprehensive test for all template endpoints
"""

import requests
import json
from typing import Optional

# Base URL
BASE_URL = "http://localhost:8000"

# JWT Token from user (Fresh token - expires at 2025-01-25 18:20:27 UTC)
JWT_TOKEN = "eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18zNUttWDBKTXBsbURzdmRJWkJFbk5VTU9BdUsiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwOi8vbG9jYWxob3N0OjMwMDAiLCJleHAiOjE3NjQwNzQ4MjcsImZ2YSI6WzEzMDUsLTFdLCJpYXQiOjE3NjQwNzQ3NjcsImlzcyI6Imh0dHBzOi8vYXB0LWNsYW0tNTMuY2xlcmsuYWNjb3VudHMuZGV2IiwibmJmIjoxNzY0MDc0NzU3LCJvIjp7ImlkIjoib3JnXzM1am1kN0x2MzE3SHpFWkE2OEZlUVJ1azZPbCIsInJvbCI6ImFkbWluIiwic2xnIjoiY29kZW11cmYtMTc2MzYzMTkzOSJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsInNpZCI6InNlc3NfMzV2aE12SnZWMDVLRzRDcEhwVkUwRmxReEdSIiwic3RzIjoiYWN0aXZlIiwic3ViIjoidXNlcl8zNWptYUhiNEE0Z0lqRHRiYTlhWk5JdGVGbkYiLCJ2IjoyfQ.p-do9y9A0PWqQcaoiFaPtceqQE34qRrWC1UTV2qmspzLzw2To0B0ud1bzzfdOZCRnXpJ5UiJlB6Zt3Diy14pyUKlD0I9fJBgvGF4j6IlrC-rg7y3AVgHL1kxdRK9RV4s4jnPkwzMdPFRHFWwWzqLTrJF3BJxwTddo8Uon0CB1sdAWti-eIjaJiLLaSAqOMWrELNsbV7-tVgPliA_Cc227puySivID7YlvKUZUqG6aIMU0GD80jRUc53nd-yXDGUSlczHHqp6RMqzm-ItkbsiKq5zWeyT9RCS1j-rdRsuloNBprIsb_KLOiFudF5RBLhr7qQy6BvFrWZ-Z5S5vw3vCA"


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


def test_get_all_templates():
    """Test GET /api/templates/"""
    print_header("TEST 1: Get All Templates")
    
    url = f"{BASE_URL}/api/templates/"
    
    try:
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Successfully fetched templates")
            print(f"\nResponse Data:")
            print(f"  Total templates: {data.get('total', 'N/A')}")
            print(f"  Templates in response: {len(data.get('templates', []))}")
            
            if data.get('templates') and len(data['templates']) > 0:
                print(f"\nFirst template:")
                first = data['templates'][0]
                print(f"  ID: {first.get('id')}")
                print(f"  Title: {first.get('title')}")
                print(f"  Category: {first.get('category')}")
                print(f"  Type: {first.get('type')}")
                
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_get_template_by_id(template_id: str):
    """Test GET /api/templates/{id}"""
    print_header(f"TEST 2: Get Template by ID ({template_id})")
    
    url = f"{BASE_URL}/api/templates/{template_id}"
    
    try:
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Successfully fetched template {template_id}")
            print(f"\nTemplate Data:")
            template = data.get('template', data)
            print(f"  ID: {template.get('id')}")
            print(f"  Title: {template.get('title')}")
            print(f"  Category: {template.get('category')}")
            print(f"  Type: {template.get('type')}")
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_create_template():
    """Test POST /api/templates/"""
    print_header("TEST 3: Create New Template")
    
    url = f"{BASE_URL}/api/templates/"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    template_data = {
        "title": "Test Template from API",
        "short_description": "A test template created via API with JWT token",
        "full_description": "This is a comprehensive test template created via API to verify JWT authentication and template creation functionality.",
        "category": "Web Development",
        "type": "Full Stack",
        "language": "JavaScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "pricing_inr": 0,
        "pricing_usd": 0,
        "code": "// Test template code\nconst app = express();\napp.listen(3000);",
        "tags": ["test", "api", "jwt", "express"],
        "developer_name": "API Tester",
        "developer_experience": "5 years",
        "is_available_for_dev": True,
        "featured": False,
        "preview_images": [],
        "dependencies": ["express", "nodejs"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=template_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_result(True, "Successfully created template")
            print(f"\nCreated Template:")
            print(json.dumps(data, indent=2)[:500] + "...")
            
            # Extract template ID for further testing
            if 'template' in data and 'id' in data['template']:
                template_id = data['template']['id']
            elif 'id' in data:
                template_id = data['id']
            elif '_id' in data:
                template_id = data['_id']
            else:
                template_id = None
                
            if template_id:
                print(f"\n{Colors.YELLOW}Template ID: {template_id}{Colors.RESET}")
                return template_id
            else:
                print(f"\n{Colors.RED}Warning: Could not extract template ID from response{Colors.RESET}")
                return None
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_update_template(template_id: str):
    """Test PUT /api/templates/{id}"""
    print_header(f"TEST 4: Update Template ({template_id})")
    
    url = f"{BASE_URL}/api/templates/{template_id}"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "title": "Updated Test Template",
        "short_description": "This template has been updated via API"
    }
    
    try:
        response = requests.put(url, headers=headers, json=update_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Successfully updated template {template_id}")
            print(f"\nUpdated Template:")
            print(json.dumps(data, indent=2)[:500] + "...")
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_delete_template(template_id: str):
    """Test DELETE /api/templates/{id}"""
    print_header(f"TEST 5: Delete Template ({template_id})")
    
    url = f"{BASE_URL}/api/templates/{template_id}"
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    try:
        response = requests.delete(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 204]:
            print_result(True, f"Successfully deleted template {template_id}")
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


def test_get_my_templates():
    """Test GET /api/templates/my"""
    print_header("TEST 6: Get My Templates")
    
    url = f"{BASE_URL}/api/templates/my"
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Successfully fetched my templates")
            print(f"\nMy Templates:")
            print(f"  Total: {data.get('pagination', {}).get('total', 'N/A')}")
            
            templates = data.get('templates', [])
            if templates:
                for i, tmpl in enumerate(templates[:3], 1):  # Show first 3
                    print(f"\n  Template {i}:")
                    print(f"    ID: {tmpl.get('id', tmpl.get('_id'))}")
                    print(f"    Title: {tmpl.get('title')}")
                    print(f"    Category: {tmpl.get('category')}")
            else:
                print("\n  No templates found")
                
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_get_template_categories():
    """Test GET /api/templates/categories"""
    print_header("TEST 7: Get Template Categories")
    
    url = f"{BASE_URL}/api/templates/categories"
    
    try:
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Successfully fetched template categories")
            print(f"\nCategories:")
            categories = data.get('categories', [])
            for cat in categories[:10]:  # Show first 10
                print(f"  - {cat}")
            if len(categories) > 10:
                print(f"  ... and {len(categories) - 10} more")
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            return None
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        return None


def test_get_template_stats():
    """Test GET /api/templates/stats/overview"""
    print_header("TEST 8: Get Template Stats")
    
    url = f"{BASE_URL}/api/templates/stats/overview"
    
    try:
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Successfully fetched template stats")
            print(f"\nStats:")
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


def test_get_favorite_templates():
    """Test GET /api/templates/favorites"""
    print_header("TEST 9: Get Favorite Templates")
    
    url = f"{BASE_URL}/api/templates/favorites"
    headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Successfully fetched favorite templates")
            print(f"\nFavorite Templates:")
            print(f"  Total: {data.get('pagination', {}).get('total', 'N/A')}")
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
    """Run all template API tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                      TEMPLATE API TEST WITH JWT TOKEN                        ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Using JWT Token (first 50 chars): {JWT_TOKEN[:50]}...{Colors.RESET}\n")
    
    # Test 1: Get all templates
    templates = test_get_all_templates()
    
    # Test 2: Get specific template (if any exist)
    if templates and templates.get('templates') and len(templates['templates']) > 0:
        first_template_id = templates['templates'][0].get('id') or templates['templates'][0].get('_id')
        if first_template_id:
            test_get_template_by_id(str(first_template_id))
    
    # Test 3: Create a new template
    created_id = test_create_template()
    
    # Test 4 & 5: Update and delete the created template
    if created_id:
        test_update_template(str(created_id))
        
        # Verify the update worked
        test_get_template_by_id(str(created_id))
        
        # Clean up - delete the test template
        test_delete_template(str(created_id))
    
    # Test 6: Get my templates
    test_get_my_templates()
    
    # Test 7: Get template categories
    test_get_template_categories()
    
    # Test 8: Get template stats
    test_get_template_stats()
    
    # Test 9: Get favorite templates
    test_get_favorite_templates()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                            TESTS COMPLETED                                    ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")


if __name__ == "__main__":
    main()
