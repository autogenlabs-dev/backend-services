"""
Complete Template Creation Demo
Shows: Create developer account -> Upgrade role -> Create template
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import hashlib

async def setup_developer_and_create_template():
    """Complete setup: developer account + template creation"""
    
    print("\n" + "="*70)
    print("  TEMPLATE CREATION - COMPLETE DEMO")
    print("="*70 + "\n")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['user_management']
    
    # Step 1: Create or find developer user
    print("Step 1: Setting up developer account...")
    
    email = "developer@example.com"
    password = "DevPassword123!"
    
    # Hash password (bcrypt-like simulation - use proper bcrypt in production)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(password)
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": email})
    
    if existing_user:
        print(f"   Found existing user: {email}")
        user_id = existing_user["_id"]
        
        # Upgrade to developer if not already
        if existing_user.get("role") != "developer":
            await db.users.update_one(
                {"_id": user_id},
                {"$set": {"role": "developer"}}
            )
            print(f"   Upgraded to developer role")
        else:
            print(f"   Already has developer role")
    else:
        # Create new developer user
        user_doc = {
            "email": email,
            "username": "developer",
            "hashed_password": hashed_password,
            "role": "developer",  # Start with developer role
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await db.users.insert_one(user_doc)
        user_id = result.inserted_id
        print(f"   Created new developer: {email}")
    
    print(f"   User ID: {user_id}")
    print(f"   Credentials: {email} / {password}\n")
    
    # Step 2: Create a sample template
    print("Step 2: Creating sample template...")
    
    template_doc = {
        "title": "Modern React Dashboard",
        "category": "Dashboard",
        "type": "React",
        "language": "TypeScript",
        "difficulty_level": "Medium",
        "plan_type": "Free",
        "rating": 0.0,
        "downloads": 0,
        "views": 0,
        "likes": 0,
        "pricing_inr": 0,
        "pricing_usd": 0,
        "short_description": "A professional React dashboard template with charts and analytics",
        "full_description": """
# Modern React Dashboard

A complete, production-ready dashboard template built with:
- **React 18** with TypeScript
- **TailwindCSS** for styling
- **Recharts** for data visualization
- **React Router** for navigation
- **Redux Toolkit** for state management

## Features
- Responsive design
- Dark mode support
- Real-time charts
- User authentication
- API integration ready
- Clean code architecture

Perfect for admin panels, analytics dashboards, and data-driven applications.
        """.strip(),
        "preview_images": [],
        "git_repo_url": "https://github.com/example/react-dashboard-template",
        "live_demo_url": "https://react-dashboard-demo.vercel.app",
        "dependencies": [
            "react@18.2.0",
            "typescript@5.0.0",
            "tailwindcss@3.3.0",
            "recharts@2.5.0",
            "@reduxjs/toolkit@1.9.0",
            "react-router-dom@6.10.0"
        ],
        "tags": [
            "dashboard",
            "admin",
            "charts",
            "analytics",
            "react",
            "typescript",
            "tailwindcss"
        ],
        "developer_name": "Test Developer",
        "developer_experience": "5+ years of React development experience",
        "is_available_for_dev": True,
        "featured": False,
        "popular": False,
        "user_id": user_id,
        "code": """
// src/Dashboard.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const Dashboard: React.FC = () => {
  const data = [
    { month: 'Jan', value: 400 },
    { month: 'Feb', value: 300 },
    { month: 'Mar', value: 600 },
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <LineChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#8884d8" />
      </LineChart>
    </div>
  );
};

export default Dashboard;
        """.strip(),
        "readme_content": """
# React Dashboard Template

## Installation

```bash
npm install
npm run dev
```

## Features

- Modern React 18
- TypeScript for type safety
- TailwindCSS for styling
- Recharts for charts
- Fully responsive

## License

MIT
        """.strip(),
        "approval_status": "approved",  # Auto-approve for demo
        "is_purchasable": True,
        "purchase_count": 0,
        "average_rating": 0.0,
        "total_ratings": 0,
        "comments_count": 0,
        "rating_distribution": {
            "5_star": 0,
            "4_star": 0,
            "3_star": 0,
            "2_star": 0,
            "1_star": 0
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Check if template exists
    existing_template = await db.templates.find_one({"title": template_doc["title"]})
    
    if existing_template:
        template_id = existing_template["_id"]
        print(f"   Template already exists: {template_id}")
    else:
        result = await db.templates.insert_one(template_doc)
        template_id = result.inserted_id
        print(f"   Created template: {template_id}")
    
    print(f"   Title: {template_doc['title']}")
    print(f"   Category: {template_doc['category']}")
    print(f"   Type: {template_doc['type']}\n")
    
    # Step 3: Verify via API
    print("Step 3: Verification...")
    print(f"   Login at: http://localhost:8000/api/auth/login")
    print(f"   Email: {email}")
    print(f"   Password: {password}\n")
    
    # Step 4: Show how to use
    print("="*70)
    print("  HOW TO CREATE MORE TEMPLATES")
    print("="*70 + "\n")
    
    print("Method 1: Via API (Recommended)")
    print("-" * 70)
    print("""
import httpx

async def create_template():
    async with httpx.AsyncClient() as client:
        # Login
        response = await client.post(
            'http://localhost:8000/api/auth/login',
            data={'username': 'developer@example.com', 'password': 'DevPassword123!'}
        )
        token = response.json()['access_token']
        
        # Create template
        headers = {'Authorization': f'Bearer {token}'}
        template = {
            'title': 'Vue.js E-commerce Template',
            'category': 'E-commerce',
            'type': 'Vue',
            'language': 'JavaScript',
            'difficulty_level': 'Easy',
            'plan_type': 'Free',
            'pricing_inr': 0,
            'pricing_usd': 0,
            'short_description': 'Complete e-commerce solution',
            'full_description': 'Full-featured online store template',
            'developer_name': 'Test Developer',
            'developer_experience': '5+ years',
            'git_repo_url': 'https://github.com/example/vue-shop',
            'live_demo_url': 'https://vue-shop-demo.vercel.app',
            'dependencies': ['vue', 'vuex', 'vue-router'],
            'tags': ['ecommerce', 'shop', 'vue']
        }
        
        response = await client.post(
            'http://localhost:8000/api/templates/',
            json=template,
            headers=headers
        )
        print(response.json())
    """)
    
    print("\nMethod 2: Via Frontend (React + Clerk)")
    print("-" * 70)
    print("""
import { useAuth } from '@clerk/nextjs';

export function CreateTemplate() {
  const { getToken } = useAuth();
  
  const handleSubmit = async (formData) => {
    const token = await getToken();
    
    const response = await fetch('http://localhost:8000/api/templates/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    if (response.ok) {
      const data = await response.json();
      alert('Template created!');
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
    """)
    
    print("\n" + "="*70)
    print("  TEST THE TEMPLATE")
    print("="*70 + "\n")
    
    print("1. View all templates:")
    print("   curl http://localhost:8000/api/templates/\n")
    
    print("2. View specific template:")
    print(f"   curl http://localhost:8000/api/templates/{template_id}\n")
    
    print("3. View categories:")
    print("   curl http://localhost:8000/api/templates/categories/list\n")
    
    print("4. View stats:")
    print("   curl http://localhost:8000/api/templates/stats/overview\n")
    
    print("="*70)
    print("  SUMMARY")
    print("="*70 + "\n")
    
    print("Created:")
    print(f"  - Developer account: {email}")
    print(f"  - Template: {template_doc['title']}")
    print(f"  - Template ID: {template_id}")
    print(f"\nCredentials:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"\nAccess Level:")
    print(f"  Role: developer")
    print(f"  Can create templates: Yes")
    print(f"  Can update own templates: Yes")
    print(f"\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_developer_and_create_template())
