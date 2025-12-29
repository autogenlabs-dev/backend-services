"""
Script to add Tailwind CSS components to the database.
Beautiful, modern Tailwind components that work with the CDN.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from bson import ObjectId
from datetime import datetime, timezone

load_dotenv()

MONGODB_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/user_management_db")

# Tailwind CSS components
TAILWIND_COMPONENTS = [
    # BUTTONS
    {
        "name": "Gradient Button",
        "category": "Buttons",
        "description": "Beautiful gradient button with hover effects using Tailwind CSS.",
        "framework": "Tailwind CSS",
        "html": """<button class="relative inline-flex items-center justify-center px-8 py-3 overflow-hidden font-medium text-white transition-all duration-300 ease-out bg-gradient-to-r from-purple-600 to-blue-500 rounded-full shadow-lg group hover:from-purple-500 hover:to-blue-400 hover:shadow-xl hover:scale-105">
  <span class="relative flex items-center gap-2">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
    </svg>
    Get Started
  </span>
</button>""",
        "css": "",
        "tags": ["button", "gradient", "tailwind", "modern"],
    },
    {
        "name": "Outline Button Group",
        "category": "Buttons",
        "description": "Elegant outline button group with multiple variants.",
        "framework": "Tailwind CSS",
        "html": """<div class="flex gap-4 flex-wrap">
  <button class="px-6 py-2.5 border-2 border-purple-500 text-purple-500 font-semibold rounded-lg hover:bg-purple-500 hover:text-white transition-all duration-300">
    Primary
  </button>
  <button class="px-6 py-2.5 border-2 border-emerald-500 text-emerald-500 font-semibold rounded-lg hover:bg-emerald-500 hover:text-white transition-all duration-300">
    Success
  </button>
  <button class="px-6 py-2.5 border-2 border-rose-500 text-rose-500 font-semibold rounded-lg hover:bg-rose-500 hover:text-white transition-all duration-300">
    Danger
  </button>
</div>""",
        "css": "",
        "tags": ["button", "outline", "group", "tailwind"],
    },
    # CARDS
    {
        "name": "Profile Card",
        "category": "Cards",
        "description": "Modern profile card with avatar, social links, and gradient background.",
        "framework": "Tailwind CSS",
        "html": """<div class="w-72 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-2xl overflow-hidden shadow-2xl">
  <div class="h-24 bg-gradient-to-r from-violet-600 to-indigo-600"></div>
  <div class="px-6 pb-6 relative">
    <div class="w-20 h-20 bg-gradient-to-br from-violet-400 to-indigo-600 rounded-full border-4 border-slate-900 -mt-10 flex items-center justify-center text-white text-2xl font-bold">
      JD
    </div>
    <h3 class="text-xl font-bold text-white mt-3">John Doe</h3>
    <p class="text-violet-300 text-sm">Senior Developer</p>
    <p class="text-gray-400 text-sm mt-3">Building amazing products with React & Node.js 🚀</p>
    <div class="flex gap-3 mt-4">
      <a href="#" class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center text-gray-400 hover:bg-violet-600 hover:text-white transition-all">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
      </a>
      <a href="#" class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center text-gray-400 hover:bg-blue-500 hover:text-white transition-all">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
      </a>
      <a href="#" class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center text-gray-400 hover:bg-blue-700 hover:text-white transition-all">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
      </a>
    </div>
  </div>
</div>""",
        "css": "",
        "tags": ["card", "profile", "social", "tailwind", "gradient"],
    },
    {
        "name": "Pricing Card",
        "category": "Cards",
        "description": "Premium pricing card with features list and CTA button.",
        "framework": "Tailwind CSS",
        "html": """<div class="w-80 bg-gradient-to-b from-slate-800 to-slate-900 rounded-2xl p-8 border border-slate-700 relative overflow-hidden">
  <div class="absolute top-0 right-0 bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-xs font-bold px-4 py-1 rounded-bl-lg">POPULAR</div>
  <h3 class="text-gray-400 font-semibold uppercase tracking-wider text-sm">Pro Plan</h3>
  <div class="mt-4 flex items-baseline gap-1">
    <span class="text-5xl font-bold text-white">$29</span>
    <span class="text-gray-400">/month</span>
  </div>
  <p class="text-gray-400 mt-4 text-sm">Perfect for growing businesses and teams.</p>
  <ul class="mt-6 space-y-3">
    <li class="flex items-center gap-3 text-gray-300">
      <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
      Unlimited projects
    </li>
    <li class="flex items-center gap-3 text-gray-300">
      <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
      Priority support
    </li>
    <li class="flex items-center gap-3 text-gray-300">
      <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
      50GB storage
    </li>
    <li class="flex items-center gap-3 text-gray-300">
      <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
      Advanced analytics
    </li>
  </ul>
  <button class="w-full mt-8 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold rounded-xl hover:opacity-90 transition-opacity">
    Get Started
  </button>
</div>""",
        "css": "",
        "tags": ["card", "pricing", "saas", "tailwind"],
    },
    # INPUTS
    {
        "name": "Modern Input Field",
        "category": "Inputs",
        "description": "Sleek input field with icon and focus animation.",
        "framework": "Tailwind CSS",
        "html": """<div class="w-80">
  <label class="block text-gray-400 text-sm font-medium mb-2">Email Address</label>
  <div class="relative">
    <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
      <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"/>
      </svg>
    </div>
    <input type="email" placeholder="you@example.com" 
      class="w-full pl-12 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"/>
  </div>
</div>""",
        "css": "",
        "tags": ["input", "form", "email", "tailwind"],
    },
    {
        "name": "Search Input",
        "category": "Inputs",
        "description": "Stylish search input with icon and keyboard shortcut hint.",
        "framework": "Tailwind CSS",
        "html": """<div class="relative w-96">
  <input type="text" placeholder="Search..." 
    class="w-full pl-12 pr-20 py-3 bg-slate-800 border border-slate-700 rounded-2xl text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all"/>
  <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
    <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
    </svg>
  </div>
  <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
    <kbd class="px-2 py-1 bg-slate-700 rounded text-xs text-gray-400 font-mono">⌘K</kbd>
  </div>
</div>""",
        "css": "",
        "tags": ["input", "search", "tailwind", "modern"],
    },
    # BADGES & ALERTS
    {
        "name": "Status Badges",
        "category": "Badges",
        "description": "Colorful status badges with dot indicators.",
        "framework": "Tailwind CSS",
        "html": """<div class="flex flex-wrap gap-3">
  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-emerald-500/10 text-emerald-400 ring-1 ring-inset ring-emerald-500/20">
    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
    Active
  </span>
  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-amber-500/10 text-amber-400 ring-1 ring-inset ring-amber-500/20">
    <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
    Pending
  </span>
  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-rose-500/10 text-rose-400 ring-1 ring-inset ring-rose-500/20">
    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
    Inactive
  </span>
  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium bg-violet-500/10 text-violet-400 ring-1 ring-inset ring-violet-500/20">
    <span class="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse"></span>
    Live
  </span>
</div>""",
        "css": "",
        "tags": ["badge", "status", "tailwind", "indicator"],
    },
    {
        "name": "Notification Alert",
        "category": "Alerts",
        "description": "Modern notification alert with icon and close button.",
        "framework": "Tailwind CSS",
        "html": """<div class="w-96 flex items-start gap-4 p-4 bg-gradient-to-r from-violet-600/10 to-indigo-600/10 border border-violet-500/20 rounded-xl">
  <div class="flex-shrink-0 w-10 h-10 bg-violet-500/20 rounded-full flex items-center justify-center">
    <svg class="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
    </svg>
  </div>
  <div class="flex-1">
    <h4 class="text-white font-semibold">New Update Available</h4>
    <p class="text-gray-400 text-sm mt-1">A new version of the app is ready. Click to update now.</p>
  </div>
  <button class="text-gray-500 hover:text-white transition-colors">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
    </svg>
  </button>
</div>""",
        "css": "",
        "tags": ["alert", "notification", "tailwind", "toast"],
    },
    # AVATARS & LISTS
    {
        "name": "Avatar Group",
        "category": "Avatars",
        "description": "Stacked avatar group with overflow indicator.",
        "framework": "Tailwind CSS",
        "html": """<div class="flex items-center">
  <div class="flex -space-x-3">
    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-rose-500 ring-2 ring-slate-900 flex items-center justify-center text-white text-sm font-bold">A</div>
    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-500 ring-2 ring-slate-900 flex items-center justify-center text-white text-sm font-bold">B</div>
    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 ring-2 ring-slate-900 flex items-center justify-center text-white text-sm font-bold">C</div>
    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 ring-2 ring-slate-900 flex items-center justify-center text-white text-sm font-bold">D</div>
    <div class="w-10 h-10 rounded-full bg-slate-700 ring-2 ring-slate-900 flex items-center justify-center text-gray-300 text-xs font-medium">+5</div>
  </div>
  <span class="ml-4 text-gray-400 text-sm">9 members</span>
</div>""",
        "css": "",
        "tags": ["avatar", "group", "tailwind", "team"],
    },
    {
        "name": "Stats Card",
        "category": "Cards",
        "description": "Dashboard stats card with icon, value, and trend indicator.",
        "framework": "Tailwind CSS",
        "html": """<div class="w-64 p-6 bg-slate-800/50 rounded-2xl border border-slate-700">
  <div class="flex items-center justify-between">
    <div class="w-12 h-12 bg-violet-500/20 rounded-xl flex items-center justify-center">
      <svg class="w-6 h-6 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
    </div>
    <span class="flex items-center gap-1 text-emerald-400 text-sm font-medium">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
      </svg>
      +12.5%
    </span>
  </div>
  <div class="mt-4">
    <p class="text-gray-400 text-sm">Total Revenue</p>
    <p class="text-3xl font-bold text-white mt-1">$48,250</p>
  </div>
</div>""",
        "css": "",
        "tags": ["card", "stats", "dashboard", "tailwind"],
    },
]

async def add_tailwind_components():
    """Add Tailwind CSS components to database."""
    
    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_default_database()
    components_collection = db.components
    
    # Get user_id
    sample = await components_collection.find_one({'user_id': {'$exists': True}})
    user_id = sample.get('user_id') if sample else ObjectId("000000000000000000000001")
    
    added_count = 0
    for comp in TAILWIND_COMPONENTS:
        # Check if already exists
        existing = await components_collection.find_one({"name": comp["name"]})
        if existing:
            print(f"⏭️ Skipping (exists): {comp['name']}")
            continue
        
        # Create component document with code as object
        component_doc = {
            "_id": ObjectId(),
            "name": comp["name"],
            "title": comp["name"],
            "category": comp["category"],
            "description": comp["description"],
            "short_description": comp["description"],
            "framework": comp["framework"],
            "html_code": comp["html"],
            "css_code": comp["css"],
            "code": {"html": comp["html"], "css": comp["css"]},  # Object format for API
            "tags": comp["tags"],
            "type": "Tailwind",
            "language": "Tailwind CSS",
            "difficulty_level": "Easy",
            "plan_type": "Free",
            "full_description": "",
            "developer_name": "Tailwind Community",
            "developer_experience": "3",
            "views": 0,
            "downloads": 0,
            "likes": 0,
            "rating": 4.7,
            "is_active": True,
            "approval_status": "approved",
            "is_premium": False,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        await components_collection.insert_one(component_doc)
        print(f"✅ Added: {comp['name']} ({comp['category']})")
        added_count += 1
    
    total = await components_collection.count_documents({})
    print(f"\n📊 Added: {added_count} Tailwind components")
    print(f"📊 Total: {total} components")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_tailwind_components())
    print("\n🎉 Done!")
