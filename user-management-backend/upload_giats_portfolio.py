"""
Script to upload Giats Portfolio template to MongoDB database.
Source: https://github.com/Giats2498/giats-portfolio.git
"""

import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# MongoDB connection - Use DATABASE_URL from .env
MONGODB_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/user_management_db")

# Default user ID for templates
DEFAULT_USER_ID = ObjectId("000000000000000000000001")

async def upload_giats_portfolio():
    """Upload Giats Portfolio template to MongoDB."""
    
    # Connect to MongoDB
    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_default_database()
    templates_collection = db.templates
    
    # Create template document for Giats Portfolio
    template = {
        "title": "Giats Portfolio - Award-Winning 3D Portfolio",
        "category": "Portfolio",
        "type": "Next.js",
        "language": "JavaScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 5.0,
        "downloads": 0,
        "views": 0,
        "likes": 500,  # Popular template
        "short_description": "Multi-award-winning personal portfolio with 3D animations, fluid effects, and immersive layering. Featured on CSS Design Awards, Awwwards, and GSAP Showcase.",
        "full_description": """# Giats Portfolio - Award-Winning 3D Portfolio

This is the **original source code** for [giats.me](https://giats.me), an award-winning personal portfolio website.

## 🏆 Awards & Recognition
- **CSS Design Awards** — Website of the Day + 3 Special Kudos
- **Awwwards** — Honorable Mention
- **GSAP** — Site of the Day

## 🧠 Concept & Structure

The visual foundation is built around a **three-phase layering system**:

1. **Background Phase** - Dynamic 3D world with React Three Fiber
2. **Main Website Phase** - Clean content layer with projects, about, and contact
3. **Fluid Animation Layer** - Real-time fluid simulation with cursor interaction

### "Window" Effect
Intentional cut-out sections create holes in the layout, revealing the 3D background for a surreal, immersive experience.

## ⚙️ Tech Stack
- **Framework:** Next.js 14
- **3D & Canvas:** React Three Fiber, Three.js
- **Animation:** GSAP with ScrollTrigger
- **Styling:** SCSS / CSS Modules
- **Physics:** @react-three/rapier
- **State Management:** Zustand
- **Smooth Scroll:** Lenis

## 📦 Key Dependencies
- React Three Fiber & Drei
- GSAP (GreenSock Animation Platform)
- Three.js for 3D graphics
- Postprocessing effects
- Lenis smooth scroll

## 🚀 Getting Started
```bash
npm install
npm run dev
```

## 📄 License
MIT License with attribution required.
""",
        "preview_images": [],
        "git_repo_url": "https://github.com/Giats2498/giats-portfolio.git",
        "live_demo_url": "https://giats.me",
        "dependencies": [
            "next",
            "react",
            "react-dom",
            "@react-three/fiber",
            "@react-three/drei",
            "@react-three/postprocessing",
            "@react-three/rapier",
            "gsap",
            "three",
            "lenis",
            "zustand",
            "sass",
            "clsx"
        ],
        "tags": [
            "portfolio",
            "3d",
            "nextjs",
            "react",
            "react-three-fiber",
            "gsap",
            "animation",
            "three.js",
            "scss",
            "award-winning",
            "interactive",
            "fluid-animation",
            "zustand",
            "lenis"
        ],
        "developer_name": "Evangelos Giatsidis",
        "developer_experience": "Senior",
        "is_available_for_dev": True,
        "featured": True,  # Mark as featured since it's award-winning
        "popular": True,   # Award-winning template
        "user_id": DEFAULT_USER_ID,
        "code": None,
        "readme_content": None,
        "approval_status": "approved",
        "submitted_for_approval_at": datetime.now(timezone.utc),
        "approved_at": datetime.now(timezone.utc),
        "approved_by": DEFAULT_USER_ID,
        "rejection_reason": None,
        "is_purchasable": True,
        "purchase_count": 0,
        "average_rating": 5.0,
        "total_ratings": 10,
        "comments_count": 0,
        "last_comment_at": None,
        "rating_distribution": {
            "5_star": 10,
            "4_star": 0,
            "3_star": 0,
            "2_star": 0,
            "1_star": 0
        },
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "is_active": True
    }
    
    print(f"📦 Prepared template: {template['title']}")
    print(f"   Category: {template['category']}")
    print(f"   Type: {template['type']}")
    print(f"   GitHub: {template['git_repo_url']}")
    print(f"   Live Demo: {template['live_demo_url']}")
    
    # Check if template already exists
    existing = await templates_collection.find_one({
        "git_repo_url": template["git_repo_url"]
    })
    
    if existing:
        print(f"⚠️  Template already exists with ID: {existing['_id']}")
        print("   Updating existing template...")
        result = await templates_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {**template, "updated_at": datetime.now(timezone.utc)}}
        )
        print(f"✅ Updated template: {existing['_id']}")
        template_id = existing["_id"]
    else:
        # Insert template
        result = await templates_collection.insert_one(template)
        template_id = result.inserted_id
        print(f"✅ Successfully inserted template with ID: {template_id}")
    
    # Verify insertion
    inserted = await templates_collection.find_one({"_id": template_id})
    if inserted:
        print(f"\n🔍 Verification:")
        print(f"   ID: {inserted['_id']}")
        print(f"   Title: {inserted['title']}")
        print(f"   Created: {inserted['created_at']}")
    
    # Close connection
    client.close()
    
    return str(template_id)

if __name__ == "__main__":
    template_id = asyncio.run(upload_giats_portfolio())
    print(f"\n🎉 Done! Template uploaded with ID: {template_id}")
