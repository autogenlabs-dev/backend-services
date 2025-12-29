"""
Upload UIverse components - Batch 3
Tailwind CSS + More CSS components
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone

MONGODB_URL = "mongodb://admin:password123@51.20.108.69:27017/user_management_db?authSource=admin"

COMPONENTS_BATCH3 = [
    # TAILWIND BUTTONS (5)
    {
        "name": "Tailwind Gradient Button",
        "category": "Buttons",
        "tags": ["tailwind", "gradient", "modern"],
        "language": "Tailwind",
        "html": """<button class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg shadow-lg hover:from-purple-600 hover:to-pink-600 transform hover:scale-105 transition-all duration-300">Get Started</button>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Outline Button",
        "category": "Buttons",
        "tags": ["tailwind", "outline", "border"],
        "language": "Tailwind",
        "html": """<button class="px-6 py-3 border-2 border-indigo-500 text-indigo-500 font-semibold rounded-lg hover:bg-indigo-500 hover:text-white transition-all duration-300">Learn More</button>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Icon Button",
        "category": "Buttons",
        "tags": ["tailwind", "icon", "circle"],
        "language": "Tailwind",
        "html": """<button class="w-12 h-12 bg-blue-500 text-white rounded-full flex items-center justify-center shadow-lg hover:bg-blue-600 hover:shadow-xl transform hover:scale-110 transition-all duration-300">+</button>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Glass Button",
        "category": "Buttons",
        "tags": ["tailwind", "glass", "blur"],
        "language": "Tailwind",
        "html": """<button class="px-6 py-3 bg-white/10 backdrop-blur-md border border-white/20 text-white font-medium rounded-xl hover:bg-white/20 transition-all duration-300">Glass Effect</button>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Pill Button",
        "category": "Buttons",
        "tags": ["tailwind", "pill", "rounded"],
        "language": "Tailwind",
        "html": """<button class="px-8 py-3 bg-emerald-500 text-white font-semibold rounded-full shadow-md hover:bg-emerald-600 hover:shadow-lg transition-all duration-300">Subscribe Now</button>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },

    # TAILWIND CARDS (5)
    {
        "name": "Tailwind Profile Card",
        "category": "Cards",
        "tags": ["tailwind", "profile", "avatar"],
        "language": "Tailwind",
        "html": """<div class="w-72 bg-gray-800 rounded-2xl p-6 text-center"><div class="w-24 h-24 mx-auto rounded-full bg-gradient-to-r from-purple-500 to-pink-500 mb-4"></div><h3 class="text-white text-xl font-bold">John Doe</h3><p class="text-gray-400 text-sm mb-4">Senior Developer</p><div class="flex justify-center gap-4"><span class="text-gray-400"><strong class="text-white">125</strong> Posts</span><span class="text-gray-400"><strong class="text-white">1.2k</strong> Followers</span></div></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Pricing Card",
        "category": "Cards",
        "tags": ["tailwind", "pricing", "plan"],
        "language": "Tailwind",
        "html": """<div class="w-72 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-8 text-white text-center"><p class="text-sm opacity-80 mb-2">PRO PLAN</p><h2 class="text-5xl font-bold mb-1">$29<span class="text-lg font-normal">/mo</span></h2><ul class="text-left text-sm space-y-3 my-6"><li>✓ Unlimited projects</li><li>✓ Priority support</li><li>✓ Custom domain</li></ul><button class="w-full py-3 bg-white text-indigo-600 font-bold rounded-xl hover:bg-gray-100 transition">Get Started</button></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Feature Card",
        "category": "Cards",
        "tags": ["tailwind", "feature", "icon"],
        "language": "Tailwind",
        "html": """<div class="w-72 bg-gray-800 border border-gray-700 rounded-2xl p-6 hover:border-indigo-500 transition-colors duration-300"><div class="w-12 h-12 bg-indigo-500/20 rounded-xl flex items-center justify-content text-2xl mb-4">⚡</div><h3 class="text-white text-lg font-bold mb-2">Lightning Fast</h3><p class="text-gray-400 text-sm leading-relaxed">Optimized for speed with sub-second load times.</p></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Blog Card",
        "category": "Cards",
        "tags": ["tailwind", "blog", "article"],
        "language": "Tailwind",
        "html": """<div class="w-80 bg-gray-800 rounded-2xl overflow-hidden"><div class="h-48 bg-gradient-to-r from-cyan-500 to-blue-500"></div><div class="p-6"><span class="px-3 py-1 bg-indigo-500/20 text-indigo-400 text-xs rounded-full">Technology</span><h3 class="text-white text-lg font-bold mt-3 mb-2">The Future of Web Dev</h3><p class="text-gray-400 text-sm">Exploring the latest trends shaping the web...</p></div></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Alert Card",
        "category": "Cards",
        "tags": ["tailwind", "alert", "notification"],
        "language": "Tailwind",
        "html": """<div class="flex items-center gap-4 w-80 bg-gray-800 border-l-4 border-green-500 rounded-lg p-4"><div class="w-10 h-10 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center">✓</div><div class="flex-1"><p class="text-white font-semibold">Success!</p><p class="text-gray-400 text-sm">Your changes saved.</p></div><button class="text-gray-500 hover:text-white text-xl">×</button></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },

    # TAILWIND INPUTS (5)
    {
        "name": "Tailwind Search Input",
        "category": "Inputs",
        "tags": ["tailwind", "search", "icon"],
        "language": "Tailwind",
        "html": """<div class="flex items-center w-72 bg-gray-800 rounded-xl px-4 py-3 border-2 border-transparent focus-within:border-indigo-500 transition-colors"><span class="text-gray-400 mr-3">🔍</span><input type="text" placeholder="Search..." class="flex-1 bg-transparent border-none outline-none text-white placeholder-gray-500"></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Email Input",
        "category": "Inputs",
        "tags": ["tailwind", "email", "form"],
        "language": "Tailwind",
        "html": """<input type="email" placeholder="Enter your email" class="w-72 px-4 py-3 bg-gray-800 border-2 border-gray-600 rounded-lg text-white outline-none focus:border-indigo-500 transition-colors placeholder-gray-500">""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Password Input",
        "category": "Inputs",
        "tags": ["tailwind", "password", "secure"],
        "language": "Tailwind",
        "html": """<div class="relative w-72"><input type="password" placeholder="Password" class="w-full px-4 py-3 pr-12 bg-gray-800 border-2 border-gray-600 rounded-lg text-white outline-none focus:border-indigo-500 transition-colors"><button class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white">👁</button></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Textarea",
        "category": "Inputs",
        "tags": ["tailwind", "textarea", "multiline"],
        "language": "Tailwind",
        "html": """<textarea placeholder="Write your message..." class="w-72 h-32 px-4 py-3 bg-gray-800 border-2 border-gray-600 rounded-xl text-white outline-none resize-none focus:border-indigo-500 transition-colors placeholder-gray-500"></textarea>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Select",
        "category": "Inputs",
        "tags": ["tailwind", "select", "dropdown"],
        "language": "Tailwind",
        "html": """<select class="w-72 px-4 py-3 bg-gray-800 border-2 border-gray-600 rounded-lg text-white outline-none focus:border-indigo-500 transition-colors cursor-pointer"><option>Select an option</option><option>Option 1</option><option>Option 2</option><option>Option 3</option></select>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },

    # CSS LOADERS (5)
    {
        "name": "Orbit Loader",
        "category": "Loaders",
        "tags": ["orbit", "planet", "rotating"],
        "language": "CSS",
        "html": """<div class="orbit-loader"><div class="planet"></div></div>""",
        "css": """.orbit-loader{width:50px;height:50px;border:3px solid #667eea;border-radius:50%;position:relative;animation:orbit-spin 2s linear infinite}.planet{position:absolute;width:12px;height:12px;background:#667eea;border-radius:50%;top:-6px;left:50%;transform:translateX(-50%)}@keyframes orbit-spin{to{transform:rotate(360deg)}}"""
    },
    {
        "name": "DNA Loader",
        "category": "Loaders",
        "tags": ["dna", "helix", "bio"],
        "language": "CSS",
        "html": """<div class="dna-loader"><span></span><span></span><span></span><span></span><span></span></div>""",
        "css": """.dna-loader{display:flex;gap:6px;align-items:center}.dna-loader span{width:8px;height:30px;background:linear-gradient(180deg,#667eea 50%,#764ba2 50%);border-radius:4px;animation:dna .8s ease-in-out infinite alternate}.dna-loader span:nth-child(2){animation-delay:.1s}.dna-loader span:nth-child(3){animation-delay:.2s}.dna-loader span:nth-child(4){animation-delay:.3s}.dna-loader span:nth-child(5){animation-delay:.4s}@keyframes dna{to{transform:scaleY(-1)}}"""
    },
    {
        "name": "Cube Loader",
        "category": "Loaders",
        "tags": ["cube", "3d", "flip"],
        "language": "CSS",
        "html": """<div class="cube-loader"></div>""",
        "css": """.cube-loader{width:40px;height:40px;background:linear-gradient(135deg,#667eea,#764ba2);animation:cube-flip 1.2s ease-in-out infinite}@keyframes cube-flip{0%{transform:perspective(120px) rotateX(0) rotateY(0)}50%{transform:perspective(120px) rotateX(-180deg) rotateY(0)}100%{transform:perspective(120px) rotateX(-180deg) rotateY(-180deg)}}"""
    },
    {
        "name": "Dots Wave Loader",
        "category": "Loaders",
        "tags": ["dots", "wave", "typing"],
        "language": "CSS",
        "html": """<div class="dots-wave"><span></span><span></span><span></span></div>""",
        "css": """.dots-wave{display:flex;gap:5px}.dots-wave span{width:10px;height:10px;background:#667eea;border-radius:50%;animation:dots-bounce .6s ease-in-out infinite}.dots-wave span:nth-child(2){animation-delay:.1s}.dots-wave span:nth-child(3){animation-delay:.2s}@keyframes dots-bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-15px)}}"""
    },
    {
        "name": "Hourglass Loader",
        "category": "Loaders",
        "tags": ["hourglass", "time", "sand"],
        "language": "CSS",
        "html": """<div class="hourglass"></div>""",
        "css": """.hourglass{width:40px;height:40px;border:3px solid #667eea;border-radius:50%;border-top-color:transparent;border-bottom-color:transparent;animation:hourglass 1s ease-in-out infinite}@keyframes hourglass{0%{transform:rotate(0)}50%{transform:rotate(180deg)}100%{transform:rotate(360deg)}}"""
    },

    # CSS FORMS (5)
    {
        "name": "Registration Form",
        "category": "Forms",
        "tags": ["register", "signup", "auth"],
        "language": "CSS",
        "html": """<form class="register-form"><h2>Create Account</h2><div class="input-row"><input type="text" placeholder="First Name"><input type="text" placeholder="Last Name"></div><input type="email" placeholder="Email"><input type="password" placeholder="Password"><button type="submit">Sign Up</button></form>""",
        "css": """.register-form{width:360px;padding:40px;background:#1a1a2e;border-radius:20px;color:#fff}.register-form h2{text-align:center;margin-bottom:30px}.input-row{display:flex;gap:12px}.register-form input{width:100%;padding:14px;margin-bottom:15px;background:#16213e;border:2px solid #1f4068;border-radius:10px;color:#fff;outline:none}.register-form input:focus{border-color:#667eea}.register-form button{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-weight:600;cursor:pointer}"""
    },
    {
        "name": "OTP Form",
        "category": "Forms",
        "tags": ["otp", "verification", "code"],
        "language": "CSS",
        "html": """<form class="otp-form"><h3>Verify Email</h3><p>Enter 4-digit code</p><div class="otp-inputs"><input type="text" maxlength="1"><input type="text" maxlength="1"><input type="text" maxlength="1"><input type="text" maxlength="1"></div><button type="submit">Verify</button></form>""",
        "css": """.otp-form{width:300px;padding:35px;background:#1a1a2e;border-radius:16px;color:#fff;text-align:center}.otp-form h3{margin-bottom:10px}.otp-form>p{opacity:.6;font-size:14px;margin-bottom:25px}.otp-inputs{display:flex;justify-content:center;gap:12px;margin-bottom:25px}.otp-inputs input{width:50px;height:55px;text-align:center;font-size:24px;background:#16213e;border:2px solid #1f4068;border-radius:10px;color:#fff;outline:none}.otp-inputs input:focus{border-color:#667eea}.otp-form button{width:100%;padding:14px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-weight:600;cursor:pointer}"""
    },
    {
        "name": "Feedback Form",
        "category": "Forms",
        "tags": ["feedback", "rating", "review"],
        "language": "CSS",
        "html": """<form class="feedback-form"><h3>Rate Experience</h3><div class="stars">⭐⭐⭐⭐⭐</div><textarea placeholder="Your feedback..."></textarea><button type="submit">Submit</button></form>""",
        "css": """.feedback-form{width:320px;padding:30px;background:#1a1a2e;border-radius:16px;color:#fff;text-align:center}.feedback-form h3{margin-bottom:20px}.stars{font-size:28px;margin-bottom:20px;cursor:pointer}.feedback-form textarea{width:100%;height:100px;padding:14px;background:#16213e;border:2px solid #1f4068;border-radius:10px;color:#fff;resize:none;outline:none;margin-bottom:15px}.feedback-form button{width:100%;padding:14px;background:#667eea;border:none;border-radius:10px;color:#fff;font-weight:600;cursor:pointer}"""
    },
    {
        "name": "Settings Form",
        "category": "Forms",
        "tags": ["settings", "preferences", "toggle"],
        "language": "CSS",
        "html": """<form class="settings-form"><h3>Preferences</h3><div class="setting"><span>Email notifications</span><input type="checkbox" checked></div><div class="setting"><span>Dark mode</span><input type="checkbox" checked></div><div class="setting"><span>Public profile</span><input type="checkbox"></div><button type="submit">Save</button></form>""",
        "css": """.settings-form{width:300px;padding:30px;background:#1a1a2e;border-radius:16px;color:#fff}.settings-form h3{margin-bottom:25px}.setting{display:flex;justify-content:space-between;align-items:center;padding:15px 0;border-bottom:1px solid #1f4068}.setting input{width:20px;height:20px;accent-color:#667eea}.settings-form button{width:100%;padding:14px;background:#667eea;border:none;border-radius:10px;color:#fff;font-weight:600;cursor:pointer;margin-top:20px}"""
    },
    {
        "name": "Upload Form",
        "category": "Forms",
        "tags": ["upload", "file", "drag"],
        "language": "CSS",
        "html": """<form class="upload-form"><div class="drop-zone"><span>📁</span><p>Drag files here</p><button type="button">Browse</button></div><button type="submit">Upload</button></form>""",
        "css": """.upload-form{width:320px;padding:25px;background:#1a1a2e;border-radius:16px;color:#fff}.drop-zone{border:2px dashed #1f4068;border-radius:12px;padding:40px 20px;text-align:center;margin-bottom:15px}.drop-zone:hover{border-color:#667eea}.drop-zone span{font-size:40px;display:block;margin-bottom:15px}.drop-zone p{opacity:.7;margin-bottom:15px}.drop-zone button{padding:10px 20px;background:#16213e;border:2px solid #1f4068;border-radius:8px;color:#fff;cursor:pointer}.upload-form>button{width:100%;padding:14px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-weight:600;cursor:pointer}"""
    },

    # TAILWIND BADGES & MISC (5)
    {
        "name": "Tailwind Badge",
        "category": "Patterns",
        "tags": ["tailwind", "badge", "tag"],
        "language": "Tailwind",
        "html": """<span class="px-3 py-1 bg-indigo-500/20 text-indigo-400 text-sm font-medium rounded-full">Featured</span>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Avatar Group",
        "category": "Patterns",
        "tags": ["tailwind", "avatar", "group"],
        "language": "Tailwind",
        "html": """<div class="flex -space-x-3"><div class="w-10 h-10 rounded-full bg-purple-500 border-2 border-gray-900"></div><div class="w-10 h-10 rounded-full bg-pink-500 border-2 border-gray-900"></div><div class="w-10 h-10 rounded-full bg-blue-500 border-2 border-gray-900"></div><div class="w-10 h-10 rounded-full bg-gray-700 border-2 border-gray-900 flex items-center justify-center text-white text-xs">+5</div></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Progress Bar",
        "category": "Patterns",
        "tags": ["tailwind", "progress", "bar"],
        "language": "Tailwind",
        "html": """<div class="w-64"><div class="flex justify-between text-sm text-gray-400 mb-2"><span>Progress</span><span>75%</span></div><div class="h-2 bg-gray-700 rounded-full overflow-hidden"><div class="h-full w-3/4 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"></div></div></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Breadcrumb",
        "category": "Patterns",
        "tags": ["tailwind", "breadcrumb", "navigation"],
        "language": "Tailwind",
        "html": """<nav class="flex items-center gap-2 text-sm"><a href="#" class="text-gray-400 hover:text-white">Home</a><span class="text-gray-600">/</span><a href="#" class="text-gray-400 hover:text-white">Products</a><span class="text-gray-600">/</span><span class="text-white">Details</span></nav>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
    {
        "name": "Tailwind Chip Group",
        "category": "Patterns",
        "tags": ["tailwind", "chip", "filter"],
        "language": "Tailwind",
        "html": """<div class="flex flex-wrap gap-2"><button class="px-4 py-2 bg-indigo-500 text-white text-sm rounded-full">All</button><button class="px-4 py-2 bg-gray-700 text-gray-300 text-sm rounded-full hover:bg-gray-600">Design</button><button class="px-4 py-2 bg-gray-700 text-gray-300 text-sm rounded-full hover:bg-gray-600">Development</button><button class="px-4 py-2 bg-gray-700 text-gray-300 text-sm rounded-full hover:bg-gray-600">Marketing</button></div>""",
        "css": "/* Tailwind CSS - Include via CDN: https://cdn.tailwindcss.com */"
    },
]


async def main():
    print("=" * 60)
    print("🎨 UIverse Components - Batch 3 (Tailwind + More)")
    print("=" * 60)
    print(f"Components to upload: {len(COMPONENTS_BATCH3)}")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.user_management_db
    collection = db.components
    
    user = await db.users.find_one({})
    user_id = user["_id"] if user else ObjectId("000000000000000000000001")
    
    added, skipped = 0, 0
    
    for comp in COMPONENTS_BATCH3:
        existing = await collection.find_one({"name": comp["name"]})
        if existing:
            print(f"  ⏭️ Exists: {comp['name']}")
            skipped += 1
            continue
        
        lang = comp.get("language", "CSS")
        doc = {
            "_id": ObjectId(),
            "name": comp["name"],
            "title": comp["name"],
            "category": comp["category"],
            "type": comp["category"],
            "language": lang,
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": f"Beautiful {comp['category'].lower()} component ({lang})",
            "full_description": f"A stunning {comp['name']} from UIverse collection",
            "developer_name": "UIverse Community",
            "developer_experience": "Community",
            "html_code": comp["html"],
            "css_code": comp["css"],
            "preview_code": f"{comp['html']}\n<style>\n{comp['css']}\n</style>",
            "code": comp["html"],
            "tags": comp["tags"],
            "views": 0,
            "downloads": 0,
            "likes": 0,
            "rating": 4.5,
            "is_active": True,
            "approval_status": "approved",
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        await collection.insert_one(doc)
        print(f"  ✅ Added: {comp['name']} ({lang})")
        added += 1
    
    total = await collection.count_documents({})
    print(f"\n📊 Added: {added} | Skipped: {skipped} | Total: {total}")
    client.close()
    print("🎉 Done!")


if __name__ == "__main__":
    asyncio.run(main())
