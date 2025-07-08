#!/usr/bin/env python3
"""
Seed Template Database
This script creates sample template data for testing.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from datetime import datetime
from bson import ObjectId

# Import models
from app.models.user import User
from app.models.template import Template, TemplateCategory
from app.config import settings

async def seed_templates():
    """Create sample template data"""
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    # Initialize Beanie
    await init_beanie(database=db, document_models=[User, Template, TemplateCategory])
    
    print("Creating sample template categories...")
    
    # Create template categories
    categories = [
        {
            "name": "Navigation",
            "display_name": "Navigation",
            "description": "Navigation components and menus",
            "icon": "🧭",
            "sort_order": 1
        },
        {
            "name": "Layout",
            "display_name": "Layout",
            "description": "Layout and grid components",
            "icon": "📐",
            "sort_order": 2
        },
        {
            "name": "Forms",
            "display_name": "Forms",
            "description": "Form components and inputs",
            "icon": "📝",
            "sort_order": 3
        },
        {
            "name": "Data Display",
            "display_name": "Data Display",
            "description": "Tables, cards, and data visualization",
            "icon": "📊",
            "sort_order": 4
        },
        {
            "name": "User Interface",
            "display_name": "User Interface",
            "description": "UI components and widgets",
            "icon": "🎨",
            "sort_order": 5
        }
    ]
    
    for cat_data in categories:
        try:
            category = TemplateCategory(**cat_data)
            await category.save()
            print(f"✓ Created category: {cat_data['name']}")
        except Exception as e:
            print(f"! Failed to create category {cat_data['name']}: {e}")
    
    print("\nCreating sample templates...")
    
    # Create a sample user if none exists
    sample_user_id = ObjectId("507f1f77bcf86cd799439011")  # Fixed ObjectId for testing
    
    # Sample templates
    templates = [
        {
            "title": "Modern Navigation Bar",
            "category": "Navigation",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Easy",
            "plan_type": "Free",
            "pricing_inr": 0,
            "pricing_usd": 0,
            "rating": 4.8,
            "downloads": 1250,
            "views": 3400,
            "likes": 89,
            "short_description": "A sleek, responsive navigation bar with dropdowns and mobile menu.",
            "full_description": "This modern navigation component features a clean design with dropdown menus, mobile hamburger menu, and smooth animations. Perfect for any modern web application.",
            "preview_images": [
                "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=400",
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400"
            ],
            "git_repo_url": "https://github.com/example/modern-navbar",
            "live_demo_url": "https://modern-navbar-demo.vercel.app",
            "dependencies": ["react", "@tailwindcss/core", "framer-motion"],
            "tags": ["navigation", "responsive", "typescript", "tailwind"],
            "developer_name": "Alex Johnson",
            "developer_experience": "5+ years",
            "is_available_for_dev": True,
            "featured": True,
            "popular": True,
            "user_id": sample_user_id,
            "code": "// Modern Navigation Component\nimport React from 'react';\n\nconst Navbar = () => {\n  return (\n    <nav className=\"bg-white shadow-lg\">\n      {/* Navigation content */}\n    </nav>\n  );\n};\n\nexport default Navbar;",
            "readme_content": "# Modern Navigation Bar\n\nA responsive navigation component built with React and Tailwind CSS.\n\n## Features\n- Mobile responsive\n- Dropdown menus\n- Smooth animations\n\n## Installation\n```bash\nnpm install\n```"
        },
        {
            "title": "Dashboard Layout",
            "category": "Layout",
            "type": "React",
            "language": "JavaScript",
            "difficulty_level": "Medium",
            "plan_type": "Paid",
            "pricing_inr": 299,
            "pricing_usd": 4,
            "rating": 4.9,
            "downloads": 890,
            "views": 2100,
            "likes": 156,
            "short_description": "Complete dashboard layout with sidebar, header, and content areas.",
            "full_description": "A comprehensive dashboard layout component featuring a collapsible sidebar, header with search and notifications, and flexible content area. Includes dark mode support and responsive design.",
            "preview_images": [
                "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400",
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400"
            ],
            "git_repo_url": "https://github.com/example/dashboard-layout",
            "live_demo_url": "https://dashboard-layout-demo.vercel.app",
            "dependencies": ["react", "tailwindcss", "lucide-react"],
            "tags": ["dashboard", "layout", "sidebar", "responsive"],
            "developer_name": "Sarah Chen",
            "developer_experience": "8+ years",
            "is_available_for_dev": True,
            "featured": True,
            "popular": False,
            "user_id": sample_user_id,
            "code": "// Dashboard Layout Component\nimport React from 'react';\n\nconst DashboardLayout = ({ children }) => {\n  return (\n    <div className=\"flex h-screen bg-gray-100\">\n      {/* Sidebar */}\n      <aside className=\"w-64 bg-white shadow-lg\">\n        {/* Sidebar content */}\n      </aside>\n      \n      {/* Main content */}\n      <main className=\"flex-1 overflow-auto\">\n        {children}\n      </main>\n    </div>\n  );\n};\n\nexport default DashboardLayout;",
            "readme_content": "# Dashboard Layout\n\nA professional dashboard layout with sidebar navigation.\n\n## Features\n- Collapsible sidebar\n- Responsive design\n- Dark mode support\n- Header with search\n\n## Usage\n```jsx\nimport DashboardLayout from './DashboardLayout';\n\nfunction App() {\n  return (\n    <DashboardLayout>\n      <h1>Dashboard Content</h1>\n    </DashboardLayout>\n  );\n}\n```"
        },
        {
            "title": "Contact Form",
            "category": "Forms",
            "type": "React",
            "language": "TypeScript",
            "difficulty_level": "Easy",
            "plan_type": "Free",
            "pricing_inr": 0,
            "pricing_usd": 0,
            "rating": 4.6,
            "downloads": 2100,
            "views": 5600,
            "likes": 203,
            "short_description": "Beautiful contact form with validation and email integration.",
            "full_description": "A clean, modern contact form component with built-in validation, error handling, and email integration. Features smooth animations and accessibility support.",
            "preview_images": [
                "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400"
            ],
            "git_repo_url": "https://github.com/example/contact-form",
            "live_demo_url": "https://contact-form-demo.vercel.app",
            "dependencies": ["react", "react-hook-form", "zod", "@tailwindcss/forms"],
            "tags": ["form", "validation", "typescript", "accessibility"],
            "developer_name": "Mike Rodriguez",
            "developer_experience": "3+ years",
            "is_available_for_dev": True,
            "featured": False,
            "popular": True,
            "user_id": sample_user_id,
            "code": "// Contact Form Component\nimport React from 'react';\nimport { useForm } from 'react-hook-form';\n\nconst ContactForm = () => {\n  const { register, handleSubmit } = useForm();\n  \n  const onSubmit = (data) => {\n    console.log(data);\n  };\n  \n  return (\n    <form onSubmit={handleSubmit(onSubmit)} className=\"space-y-4\">\n      <input {...register('name')} placeholder=\"Name\" />\n      <input {...register('email')} placeholder=\"Email\" />\n      <textarea {...register('message')} placeholder=\"Message\" />\n      <button type=\"submit\">Send Message</button>\n    </form>\n  );\n};\n\nexport default ContactForm;",
            "readme_content": "# Contact Form\n\nA beautiful contact form with validation.\n\n## Features\n- Form validation\n- Error handling\n- Email integration\n- Accessibility support\n\n## Dependencies\n- react-hook-form\n- zod\n- @tailwindcss/forms"
        }
    ]
    
    for template_data in templates:
        try:
            template = Template(**template_data)
            await template.save()
            print(f"✓ Created template: {template_data['title']}")
        except Exception as e:
            print(f"! Failed to create template {template_data['title']}: {e}")
    
    print(f"\n✅ Sample data creation complete!")
    await client.close()

if __name__ == "__main__":
    asyncio.run(seed_templates())
