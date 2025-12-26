"""
Add award-winning modern templates with 3D animations.
Verified from GitHub READMEs with clone instructions.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId

DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

# Award-winning and 3D animated templates verified from GitHub
AWARD_WINNING_TEMPLATES = [
    {
        "title": "Awwwards Winning Website - Zentry Clone",
        "category": "Landing Page",
        "type": "React Template",
        "language": "JavaScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 5.0,
        "downloads": 28000,
        "views": 85000,
        "likes": 6500,
        "short_description": "🏆 Awwwards Site of the Month winner clone with GSAP scroll animations and 3D effects",
        "full_description": """Build an Awwwards-winning animated website inspired by Zentry.com.

## 🏆 Award
This design won Awwwards Site of the Month!

## Requirements
- Node.js 18+
- npm

## Clone & Run
```bash
git clone https://github.com/adrianhajdin/award-winning-website.git
cd award-winning-website
npm install
npm run dev
```
Open http://localhost:5173

## Features
- ✨ Scroll-Based Animations with GSAP
- 🔷 Clip Path Shaped Animations
- 🎮 3D Hover Effects
- 🎬 Video Transitions
- 📱 Completely Responsive
- 🎨 Modern UI/UX

## Tech Stack
- React.js
- GSAP (GreenSock Animation Platform)
- Tailwind CSS
""",
        "git_repo_url": "https://github.com/adrianhajdin/award-winning-website",
        "live_demo_url": "https://zentry.com/",
        "dependencies": ["react", "gsap", "tailwindcss", "vite"],
        "tags": ["awwwards", "award-winning", "gsap", "animation", "3d", "scroll"],
    },
    {
        "title": "3D Interactive Portfolio - Three.js",
        "category": "Portfolio",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Advanced",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 12000,
        "views": 45000,
        "likes": 3200,
        "short_description": "🎮 Interactive 3D portfolio with physics, Three.js, and character controller",
        "full_description": """An immersive 3D portfolio experience built with Next.js and Three.js.

## Requirements
- Node.js 18+
- npm or yarn

## Clone & Run
```bash
git clone https://github.com/Alane38/3D-Nextjs-Portfolio.git
cd 3D-Nextjs-Portfolio
npm install
npm run dev
```

## 🎮 Features
### Interactive 3D Environment
- Advanced Character Controller (ARCHE)
- Dynamic platforms and obstacles
- Responsive 3D objects and animations
- Physics-based interactions (Rapier)

### Modern UI Components
- Parallax slider
- Interactive timeline
- Dynamic statistics with Chart.js
- Responsive sidebar navigation
- Project showcase sections

## Tech Stack
- Next.js 14
- Three.js + React Three Fiber
- React Three Rapier (Physics)
- Framer Motion
- TailwindCSS
- TypeScript
""",
        "git_repo_url": "https://github.com/Alane38/3D-Nextjs-Portfolio",
        "live_demo_url": "https://newalfox.dev/",
        "dependencies": ["next", "three", "react-three-fiber", "rapier", "tailwindcss"],
        "tags": ["3d", "three.js", "portfolio", "physics", "interactive", "animation"],
    },
    {
        "title": "React Three Next - 3D Starter",
        "category": "Starter Kit",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 55000,
        "views": 150000,
        "likes": 8900,
        "short_description": "🏯 Official React Three Fiber + Next.js starter for 3D web apps",
        "full_description": """The official starter template for building 3D web applications with React Three Fiber and Next.js.

## Requirements
- Node.js 18+
- Yarn (recommended)

## Clone & Run
```bash
# Using create-r3f-app (recommended)
yarn create r3f-app next my-app
cd my-app
yarn dev

# Or clone directly
git clone https://github.com/pmndrs/react-three-next
cd react-three-next
yarn install
yarn dev
```

## 🗻 Features
- GLSL shader imports
- Canvas persists between page navigation
- Canvas components in any div
- App Router architecture
- PWA Support
- TypeScript ready

## 🏗️ Architecture
Uses tunnel-rat for portaling components between renderers. 
The <View/> component renders in 3D context with gl.scissor for performance.

## ⬛ Tech Stack
- create-r3f-app
- Three.js
- @react-three/fiber
- @react-three/drei
- @react-three/a11y
- r3f-perf
""",
        "git_repo_url": "https://github.com/pmndrs/react-three-next",
        "live_demo_url": "https://react-three-next.vercel.app/",
        "dependencies": ["next", "three", "react-three-fiber", "drei"],
        "tags": ["3d", "three.js", "starter", "official", "react-three-fiber"],
    },
    {
        "title": "Modern Animated Landing Page",
        "category": "Landing Page",
        "type": "React Template",
        "language": "JavaScript",
        "difficulty_level": "Beginner",
        "plan_type": "Free",
        "rating": 4.8,
        "downloads": 18000,
        "views": 52000,
        "likes": 4100,
        "short_description": "✨ Stunning landing page with smooth GSAP animations and scroll effects",
        "full_description": """A beautiful modern landing page template with professional animations.

## Requirements
- Node.js 18+
- npm

## Clone & Run
```bash
git clone https://github.com/sherzodartikbayev/Awwwards-Winning
cd Awwwards-Winning
npm install
npm run dev
```

## Features
- 🎬 Dynamic scroll-based animations
- 🔷 Geometric CSS clip-path transitions
- 🎮 Interactive 3D hover effects
- 📱 Fully responsive design
- ⚡ Smooth performance

## Tech Stack
- React.js
- Tailwind CSS
- GSAP
""",
        "git_repo_url": "https://github.com/sherzodartikbayev/Awwwards-Winning",
        "live_demo_url": "https://zentry.com/",
        "dependencies": ["react", "gsap", "tailwindcss"],
        "tags": ["landing", "gsap", "animation", "modern", "responsive"],
    },
    {
        "title": "Cinematic Hero Landing - Framer Motion",
        "category": "Landing Page",
        "type": "Next.js Template",
        "language": "TypeScript",
        "difficulty_level": "Intermediate",
        "plan_type": "Free",
        "rating": 4.9,
        "downloads": 9500,
        "views": 32000,
        "likes": 2800,
        "short_description": "🎬 Cinematic landing page with magnetic interactions and fluid animations",
        "full_description": """High-fidelity cinematic landing page with advanced Framer Motion animations.

## Requirements
- Node.js 18+
- npm or pnpm

## Clone & Run
```bash
git clone https://github.com/Pusri27/zenith-interface
cd zenith-interface
npm install
npm run dev
```

## Features
- 🎬 Cinematic visual storytelling
- 🧲 Magnetic cursor interactions
- 🌊 Fluid motion animations
- ⚡ Next.js 15 optimized
- 🎨 Premium design aesthetic

## Tech Stack
- Next.js 15
- GSAP
- Framer Motion
- Tailwind CSS
""",
        "git_repo_url": "https://github.com/Pusri27/zenith-interface",
        "live_demo_url": "https://zenith-interface.vercel.app/",
        "dependencies": ["next", "gsap", "framer-motion", "tailwindcss"],
        "tags": ["cinematic", "landing", "framer-motion", "magnetic", "premium"],
    },
]

async def add_award_winning_templates():
    print("=" * 60)
    print("🏆 ADDING AWARD-WINNING MODERN TEMPLATES")
    print("=" * 60 + "\n")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    user = await db.users.find_one({})
    user_id = user["_id"] if user else None
    
    for tpl in AWARD_WINNING_TEMPLATES:
        template_doc = {
            "_id": ObjectId(),
            "title": tpl["title"],
            "category": tpl["category"],
            "type": tpl["type"],
            "language": tpl["language"],
            "difficulty_level": tpl["difficulty_level"],
            "plan_type": tpl["plan_type"],
            "rating": tpl["rating"],
            "downloads": tpl["downloads"],
            "views": tpl["views"],
            "likes": tpl["likes"],
            "short_description": tpl["short_description"],
            "full_description": tpl["full_description"],
            "preview_images": [],  # Will add screenshots next
            "git_repo_url": tpl["git_repo_url"],
            "live_demo_url": tpl["live_demo_url"],
            "dependencies": tpl["dependencies"],
            "tags": tpl["tags"],
            "developer_name": "Open Source Community",
            "developer_experience": "Various",
            "is_available_for_dev": True,
            "featured": True,
            "popular": True,
            "user_id": user_id,
            "approval_status": "approved",
            "approved_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True,
            "is_purchasable": True,
        }
        
        await db.templates.insert_one(template_doc)
        print(f"✅ {tpl['title']}")
        print(f"   🏷️  {', '.join(tpl['tags'][:4])}")
        print(f"   📁 {tpl['git_repo_url']}")
        print()
    
    total = await db.templates.count_documents({})
    print(f"\n📊 Total templates: {total}")
    
    client.close()
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(add_award_winning_templates())
