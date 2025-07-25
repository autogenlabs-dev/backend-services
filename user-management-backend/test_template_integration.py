#!/usr/bin/env python3
"""
Complete integration test for template APIs with authentication
"""
import asyncio
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = BASE_URL

# Test credentials (use existing user to avoid registration limits)
TEST_EMAIL = "testuser_20250720_234038@example.com"
TEST_PASSWORD = "TestPassword123!"

async def test_template_integration():
    """Test complete template API integration with authentication"""
    
    print("🚀 Testing Template API Integration")
    print("=" * 60)
    
    access_token = None
    
    try:
        # Step 1: Login to get access token
        print("\n1️⃣ Logging in to get access token...")
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        login_response = requests.post(
            f"{API_BASE}/auth/login-json",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('access_token')
            print(f"✅ Login successful! Token: {access_token[:50]}...")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return
        
        # Step 2: Test public template endpoints (no auth required)
        print("\n2️⃣ Testing public template endpoints...")
        
        # Test categories endpoint
        print("\n   📂 Testing /templates/categories...")
        categories_response = requests.get(f"{API_BASE}/templates/categories")
        
        if categories_response.status_code == 200:
            categories_data = categories_response.json()
            print("✅ Categories endpoint successful!")
            print(f"   📄 Full response: {json.dumps(categories_data, indent=2, default=str)}")
            
            # Handle different response formats
            if isinstance(categories_data, list):
                categories = categories_data
                print(f"   📊 Found {len(categories)} categories:")
                for category in categories[:5]:  # Show first 5
                    print(f"      • {category}")
                if len(categories) > 5:
                    print(f"      ... and {len(categories) - 5} more")
            elif isinstance(categories_data, dict):
                categories = categories_data.get('categories', []) or categories_data.get('data', [])
                print(f"   📊 Found {len(categories)} categories in response:")
                for category in categories[:5]:  # Show first 5
                    print(f"      • {category}")
            else:
                categories = []
                print(f"   ⚠️  Unexpected response format: {type(categories_data)}")
        else:
            print(f"❌ Categories request failed: {categories_response.status_code}")
            print(f"   Error: {categories_response.text}")
        
        # Test public templates endpoint
        print("\n   📄 Testing /templates...")
        templates_response = requests.get(f"{API_BASE}/templates")
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            print("✅ Public templates endpoint successful!")
            
            # Handle different response formats
            if isinstance(templates_data, list):
                templates = templates_data
            elif isinstance(templates_data, dict):
                templates = templates_data.get('templates', []) or templates_data.get('data', [])
            else:
                templates = []
                
            print(f"   📊 Found {len(templates)} templates:")
            for template in templates[:3]:  # Show first 3
                template_name = template.get('name', 'N/A') if isinstance(template, dict) else str(template)
                template_category = template.get('category', 'N/A') if isinstance(template, dict) else 'N/A'
                print(f"      • {template_name} (Category: {template_category})")
            if len(templates) > 3:
                print(f"      ... and {len(templates) - 3} more")
                
            # Store first template ID for detailed testing
            first_template_id = templates[0].get('id') if templates and isinstance(templates[0], dict) else None
        else:
            print(f"❌ Public templates request failed: {templates_response.status_code}")
            print(f"   Error: {templates_response.text}")
            first_template_id = None
        
        # Test template by category
        if categories:
            first_category = categories[0]
            print(f"\n   📂 Testing /templates?category={first_category}...")
            category_templates_response = requests.get(f"{API_BASE}/templates?category={first_category}")
            
            if category_templates_response.status_code == 200:
                category_templates = category_templates_response.json()
                print(f"✅ Category templates successful! Found {len(category_templates)} templates in '{first_category}'")
            else:
                print(f"❌ Category templates request failed: {category_templates_response.status_code}")
        
        # Test individual template details
        if first_template_id:
            print(f"\n   📋 Testing /templates/{first_template_id}...")
            template_detail_response = requests.get(f"{API_BASE}/templates/{first_template_id}")
            
            if template_detail_response.status_code == 200:
                template_detail = template_detail_response.json()
                print("✅ Template detail endpoint successful!")
                print(f"   Name: {template_detail.get('name', 'N/A')}")
                print(f"   Category: {template_detail.get('category', 'N/A')}")
                print(f"   Description: {template_detail.get('description', 'N/A')[:100]}...")
                print(f"   Variables: {len(template_detail.get('variables', []))} defined")
            else:
                print(f"❌ Template detail request failed: {template_detail_response.status_code}")
        
        # Step 3: Test protected template endpoints (auth required)
        if access_token:
            print("\n3️⃣ Testing protected template endpoints...")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test my templates endpoint
            print("\n   👤 Testing /templates/my...")
            my_templates_response = requests.get(f"{API_BASE}/templates/my", headers=headers)
            
            if my_templates_response.status_code == 200:
                my_templates = my_templates_response.json()
                print(f"✅ My templates endpoint successful! Found {len(my_templates)} user templates")
            else:
                print(f"❌ My templates request failed: {my_templates_response.status_code}")
                print(f"   Error: {my_templates_response.text}")
            
            # Test favorites endpoint
            print("\n   ⭐ Testing /templates/favorites...")
            favorites_response = requests.get(f"{API_BASE}/templates/favorites", headers=headers)
            
            if favorites_response.status_code == 200:
                favorites = favorites_response.json()
                print(f"✅ Favorites endpoint successful! Found {len(favorites)} favorite templates")
            else:
                print(f"❌ Favorites request failed: {favorites_response.status_code}")
                print(f"   Error: {favorites_response.text}")
        
        # Step 4: Generate frontend integration code
        print("\n4️⃣ Frontend Integration Code")
        print("=" * 60)
        
        generate_frontend_code()
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def generate_frontend_code():
    """Generate frontend integration code examples"""
    
    print("\n📱 FRONTEND INTEGRATION CODE:")
    print("-" * 40)
    
    print("\n1. Fetch categories for sidebar:")
    print("""
// React/JavaScript example
const fetchCategories = async () => {
  try {
    const response = await fetch('http://localhost:8000/templates/categories');
    const categories = await response.json();
    return categories;
  } catch (error) {
    console.error('Error fetching categories:', error);
    return [];
  }
};

// Usage in React component
const [categories, setCategories] = useState([]);

useEffect(() => {
  fetchCategories().then(setCategories);
}, []);

// Render sidebar
{categories.map(category => (
  <li key={category}>
    <a href={`/templates?category=${category}`}>
      {category}
    </a>
  </li>
))}
    """)
    
    print("\n2. Fetch templates with authentication:")
    print("""
// With authentication
const fetchUserTemplates = async (token) => {
  try {
    const response = await fetch('http://localhost:8000/templates/my', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    const templates = await response.json();
    return templates;
  } catch (error) {
    console.error('Error fetching user templates:', error);
    return [];
  }
};
    """)
    
    print("\n3. Complete sidebar component:")
    print("""
// Complete sidebar component
const TemplateSidebar = ({ onCategorySelect }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCategories = async () => {
      setLoading(true);
      const data = await fetchCategories();
      setCategories(data);
      setLoading(false);
    };
    
    loadCategories();
  }, []);

  if (loading) return <div>Loading categories...</div>;

  return (
    <div className="template-sidebar">
      <h3>Template Categories</h3>
      <ul>
        <li>
          <a href="/templates" onClick={() => onCategorySelect(null)}>
            All Templates
          </a>
        </li>
        {categories.map(category => (
          <li key={category}>
            <a 
              href={`/templates?category=${category}`}
              onClick={() => onCategorySelect(category)}
            >
              {category}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};
    """)

def test_with_curl_commands():
    """Print curl commands for manual testing"""
    print("\n" + "=" * 60)
    print("🔧 MANUAL TESTING WITH CURL")
    print("=" * 60)
    
    print("\n1. Get all categories:")
    print('curl -X GET "http://localhost:8000/templates/categories"')
    
    print("\n2. Get all public templates:")
    print('curl -X GET "http://localhost:8000/templates"')
    
    print("\n3. Get templates by category:")
    print('curl -X GET "http://localhost:8000/templates?category=Business"')
    
    print("\n4. Get specific template:")
    print('curl -X GET "http://localhost:8000/templates/{template_id}"')
    
    print("\n5. Login and get user templates:")
    print('# First login')
    print('TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login-json" \\')
    print('  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"email": "{TEST_EMAIL}", "password": "{TEST_PASSWORD}"}}\' \\')
    print('  | grep -o \'"access_token":"[^"]*"\' | cut -d\'"\' -f4)')
    print('')
    print('# Then get user templates')
    print('curl -X GET "http://localhost:8000/templates/my" \\')
    print('  -H "Authorization: Bearer $TOKEN"')
    
    print("\n6. Get favorites:")
    print('curl -X GET "http://localhost:8000/templates/favorites" \\')
    print('  -H "Authorization: Bearer $TOKEN"')

async def main():
    """Main function"""
    # Check if server is running first
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start it first:")
        print("   python run_server.py")
        print("\nAlternatively, here are curl commands for manual testing:")
        test_with_curl_commands()
        return
    except Exception as e:
        print(f"❌ Error checking server: {str(e)}")
        return
    
    await test_template_integration()
    test_with_curl_commands()

if __name__ == "__main__":
    asyncio.run(main())
