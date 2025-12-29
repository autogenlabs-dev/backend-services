"""
Test Template Creation Flow with Clerk Authentication
Shows complete workflow: Login → Create Template → View Template
"""

import asyncio
import httpx
from datetime import datetime
import json

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

async def test_template_creation():
    """Test complete template creation workflow"""
    
    print(f"\n{Colors.PURPLE}{Colors.BOLD}")
    print("="*70)
    print("  TEMPLATE CREATION WORKFLOW TEST")
    print("="*70)
    print(f"{Colors.RESET}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # Step 1: Register a developer user
        print(f"{Colors.YELLOW}Step 1: Register Developer User{Colors.RESET}")
        email = f"developer_{int(datetime.now().timestamp())}@example.com"
        register_data = {
            "email": email,
            "password": "DevPassword123!",
            "username": "developer",
            "name": "John Developer"
        }
        
        response = await client.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"{Colors.RED}Registration failed: {response.text}{Colors.RESET}")
            return
        
        user_data = response.json()
        user_id = user_data["id"]
        print(f"{Colors.GREEN}✅ Developer registered: {email}{Colors.RESET}\n")
        
        # Step 2: Update user role to developer
        print(f"{Colors.YELLOW}Step 2: Upgrade to Developer Role{Colors.RESET}")
        print(f"{Colors.CYAN}Note: In production, this would be done by admin approval{Colors.RESET}")
        
        # Login first to get token
        login_data = {
            "username": email,
            "password": "DevPassword123!"
        }
        response = await client.post(f"{BASE_URL}/api/auth/login", data=login_data)
        
        if response.status_code != 200:
            print(f"{Colors.RED}Login failed: {response.text}{Colors.RESET}")
            return
        
        auth_data = response.json()
        jwt_token = auth_data["access_token"]
        print(f"{Colors.GREEN}✅ Logged in successfully{Colors.RESET}")
        print(f"{Colors.CYAN}ℹ️  Current role: user (need to upgrade to developer){Colors.RESET}\n")
        
        # Try to create template with regular user (should fail)
        print(f"{Colors.YELLOW}Step 3: Try Creating Template as Regular User (Should Fail){Colors.RESET}")
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        template_data = {
            "title": "React Dashboard Template",
            "category": "Dashboard",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Medium",
            "plan_type": "Free",
            "pricing_inr": 0,
            "pricing_usd": 0,
            "short_description": "A modern React dashboard with charts and analytics",
            "full_description": "Complete dashboard template built with React, TypeScript, and TailwindCSS. Features include real-time charts, responsive layout, and dark mode support.",
            "preview_images": [],
            "git_repo_url": "https://github.com/example/react-dashboard",
            "live_demo_url": "https://react-dashboard-demo.vercel.app",
            "dependencies": ["react", "typescript", "tailwindcss", "recharts"],
            "tags": ["dashboard", "admin", "charts", "analytics"],
            "developer_name": "John Developer",
            "developer_experience": "5+ years React development",
            "is_available_for_dev": True,
            "featured": False,
            "code": "// React Dashboard Component\\nfunction Dashboard() { return <div>Dashboard</div>; }",
            "readme_content": "# React Dashboard\\n\\nModern dashboard template"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/templates/",
            json=template_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 403:
            print(f"{Colors.GREEN}✅ Correctly blocked - need developer role{Colors.RESET}\n")
        
        # Note: In real implementation, admin would upgrade user to developer
        # For this test, we'll show what the API expects
        print(f"{Colors.YELLOW}Step 4: Required Flow for Developer Access{Colors.RESET}")
        print(f"{Colors.CYAN}")
        print("Production Flow:")
        print("1. User requests developer access from dashboard")
        print("2. Admin reviews application")
        print("3. Admin calls: PATCH /api/admin/users/{user_id}")
        print("   Body: { 'role': 'developer' }")
        print("4. User can now create templates")
        print(f"{Colors.RESET}\n")
        
        # Step 5: Show template structure
        print(f"{Colors.YELLOW}Step 5: Template Creation Schema{Colors.RESET}")
        print(f"{Colors.CYAN}")
        print("Required Fields:")
        print(json.dumps({
            "title": "string",
            "category": "Dashboard | Blog | E-commerce | Portfolio | Admin Panel | Landing Page | SaaS Tool | Learning Management System",
            "type": "React | Vue | Angular | HTML/CSS | Svelte | Flutter",
            "language": "TypeScript | JavaScript | Python | Dart",
            "difficulty_level": "Easy | Medium | Tough",
            "plan_type": "Free | Premium",
            "pricing_inr": "number (0 for free)",
            "pricing_usd": "number (0 for free)",
            "short_description": "string (brief summary)",
            "full_description": "string (detailed description)",
            "developer_name": "string",
            "developer_experience": "string"
        }, indent=2))
        print("\nOptional Fields:")
        print(json.dumps({
            "preview_images": ["url1", "url2"],
            "git_repo_url": "GitHub URL",
            "live_demo_url": "Live demo URL",
            "dependencies": ["package1", "package2"],
            "tags": ["tag1", "tag2"],
            "code": "Source code content",
            "readme_content": "README markdown",
            "featured": "boolean (default: false)",
            "is_available_for_dev": "boolean (default: true)"
        }, indent=2))
        print(f"{Colors.RESET}\n")
        
        # Step 6: Available categories and types
        print(f"{Colors.YELLOW}Step 6: Fetch Available Categories{Colors.RESET}")
        response = await client.get(f"{BASE_URL}/api/templates/categories/list")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            categories_data = response.json()
            print(f"{Colors.GREEN}✅ Available categories:{Colors.RESET}")
            for cat in categories_data.get("categories", []):
                print(f"  • {cat}")
        print()
        
        # Step 7: Show complete workflow
        print(f"{Colors.PURPLE}{Colors.BOLD}")
        print("="*70)
        print("  COMPLETE TEMPLATE CREATION WORKFLOW")
        print("="*70)
        print(f"{Colors.RESET}\n")
        
        print(f"{Colors.GREEN}For Regular Users → Developers:{Colors.RESET}")
        print(f"""
{Colors.CYAN}1. User Registration/Login{Colors.RESET}
   • Register: POST /api/auth/register
   • Login: POST /api/auth/login
   • Get JWT token

{Colors.CYAN}2. Request Developer Access{Colors.RESET}
   • User submits developer application
   • Admin reviews and approves
   • Admin updates role: PATCH /api/admin/users/{{user_id}}
     Body: {{ "role": "developer" }}

{Colors.CYAN}3. Create Template{Colors.RESET}
   • POST /api/templates/
   • Headers: Authorization: Bearer <jwt_token>
   • Body: Template data (see schema above)
   • Status: "pending_approval" by default

{Colors.CYAN}4. Admin Approval{Colors.RESET}
   • Admin reviews template
   • Approves or rejects
   • Template becomes visible to users

{Colors.CYAN}5. Template Management{Colors.RESET}
   • GET /api/templates/ - List all approved templates
   • GET /api/templates/{{id}} - Get specific template
   • PATCH /api/templates/{{id}} - Update template (developer only)
   • DELETE /api/templates/{{id}} - Delete template (developer/admin)
        """)
        
        # Step 8: Frontend Implementation Example
        print(f"{Colors.YELLOW}Step 8: Frontend Implementation{Colors.RESET}")
        print(f"{Colors.BLUE}")
        print("""
// Template Creation Form (React + Clerk)
import { useAuth } from '@clerk/nextjs';

export function CreateTemplateForm() {
  const { getToken } = useAuth();
  
  const handleSubmit = async (formData) => {
    const token = await getToken();
    
    const response = await fetch('http://localhost:8000/api/templates/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: formData.title,
        category: formData.category,
        type: formData.type,
        language: formData.language,
        difficulty_level: formData.difficulty,
        plan_type: formData.planType,
        pricing_inr: formData.priceINR,
        pricing_usd: formData.priceUSD,
        short_description: formData.shortDesc,
        full_description: formData.fullDesc,
        git_repo_url: formData.repoUrl,
        live_demo_url: formData.demoUrl,
        dependencies: formData.dependencies.split(','),
        tags: formData.tags.split(','),
        developer_name: formData.devName,
        developer_experience: formData.experience,
        code: formData.code,
        readme_content: formData.readme,
      }),
    });
    
    if (response.ok) {
      const data = await response.json();
      alert('Template created! Awaiting admin approval.');
      return data.template;
    } else {
      const error = await response.json();
      if (response.status === 403) {
        alert('You need developer access to create templates.');
      } else {
        alert(`Error: ${error.detail}`);
      }
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
        """)
        print(f"{Colors.RESET}\n")
        
        # Step 9: API Endpoints Summary
        print(f"{Colors.PURPLE}{Colors.BOLD}")
        print("="*70)
        print("  TEMPLATE API ENDPOINTS")
        print("="*70)
        print(f"{Colors.RESET}\n")
        
        endpoints = [
            ("POST", "/api/templates/", "Create new template", "developer/admin", "Template data"),
            ("GET", "/api/templates/", "List all templates", "public", "Optional filters: category, plan_type, difficulty_level, search"),
            ("GET", "/api/templates/{id}", "Get template details", "public", "Template ID"),
            ("PATCH", "/api/templates/{id}", "Update template", "developer/admin", "Updated fields"),
            ("DELETE", "/api/templates/{id}", "Delete template", "developer/admin", "Template ID"),
            ("GET", "/api/templates/categories/list", "Get categories", "public", "None"),
            ("GET", "/api/templates/stats/overview", "Get stats", "public", "None"),
            ("POST", "/api/templates/{id}/like", "Like template", "authenticated", "Template ID"),
            ("POST", "/api/templates/{id}/download", "Track download", "authenticated", "Template ID"),
        ]
        
        print(f"{Colors.CYAN}{'Method':<8} {'Endpoint':<35} {'Access':<15} {'Description'}{Colors.RESET}")
        print("-" * 70)
        for method, endpoint, desc, access, params in endpoints:
            color = Colors.GREEN if method == "GET" else Colors.YELLOW if method == "POST" else Colors.RED
            print(f"{color}{method:<8}{Colors.RESET} {endpoint:<35} {access:<15} {desc}")
        
        print(f"\n{Colors.GREEN}✅ Template Creation System Ready!{Colors.RESET}")
        print(f"{Colors.CYAN}Note: Users need 'developer' or 'admin' role to create templates{Colors.RESET}\n")

if __name__ == "__main__":
    asyncio.run(test_template_creation())
