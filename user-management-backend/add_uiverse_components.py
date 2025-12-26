"""
Script to add UIverse-style CSS/HTML components to the database.
Components based on popular UIverse designs - buttons, cards, inputs, etc.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from bson import ObjectId
from datetime import datetime, timezone

load_dotenv()

MONGODB_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

# UIverse-style components with HTML and CSS code
UIVERSE_COMPONENTS = [
    # BUTTONS
    {
        "name": "Neon Glow Button",
        "category": "Buttons",
        "description": "Stunning neon glow button with hover animation effect. Pure CSS.",
        "framework": "CSS",
        "html_code": """<button class="neon-button">
  Click Me
</button>""",
        "css_code": """.neon-button {
  position: relative;
  padding: 12px 35px;
  background: linear-gradient(90deg, #03e9f4, #00d0ff);
  border: none;
  outline: none;
  font-size: 18px;
  letter-spacing: 4px;
  text-transform: uppercase;
  cursor: pointer;
  border-radius: 5px;
  color: #050801;
  font-weight: 600;
  box-shadow: 0 0 5px #03e9f4, 0 0 25px #03e9f4, 0 0 50px #03e9f4, 0 0 200px #03e9f4;
  transition: all 0.3s ease;
}

.neon-button:hover {
  background: transparent;
  color: #03e9f4;
  box-shadow: 0 0 5px #03e9f4, 0 0 25px #03e9f4, 0 0 50px #03e9f4, 0 0 100px #03e9f4;
}""",
        "tags": ["button", "neon", "glow", "animation"],
    },
    {
        "name": "Gradient Border Button",
        "category": "Buttons",
        "description": "Beautiful button with animated gradient border effect.",
        "framework": "CSS",
        "html_code": """<button class="gradient-button">
  <span>Explore</span>
</button>""",
        "css_code": """.gradient-button {
  position: relative;
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  background: #0f0f0f;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  z-index: 1;
}

.gradient-button::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(45deg, #ff0080, #ff8c00, #40e0d0, #ff0080);
  background-size: 400%;
  z-index: -1;
  border-radius: 10px;
  animation: gradient 8s linear infinite;
}

.gradient-button::after {
  content: '';
  position: absolute;
  inset: 2px;
  background: #0f0f0f;
  border-radius: 6px;
  z-index: -1;
}

@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}""",
        "tags": ["button", "gradient", "border", "animated"],
    },
    {
        "name": "3D Push Button",
        "category": "Buttons",
        "description": "Realistic 3D push button with depth effect on click.",
        "framework": "CSS",
        "html_code": """<button class="push-button">
  Push Me
</button>""",
        "css_code": """.push-button {
  padding: 15px 40px;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 6px 0 #4a5568, 0 8px 10px rgba(0,0,0,0.3);
  transition: all 0.1s ease;
}

.push-button:active {
  box-shadow: 0 2px 0 #4a5568, 0 4px 6px rgba(0,0,0,0.3);
  transform: translateY(4px);
}

.push-button:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}""",
        "tags": ["button", "3d", "push", "depth"],
    },
    # CARDS
    {
        "name": "Glass Morphism Card",
        "category": "Cards",
        "description": "Modern glassmorphism card with blur effect and subtle border.",
        "framework": "CSS",
        "html_code": """<div class="glass-card">
  <div class="card-icon">🚀</div>
  <h3 class="card-title">Glass Card</h3>
  <p class="card-text">Beautiful glassmorphism effect with backdrop blur.</p>
</div>""",
        "css_code": """.glass-card {
  width: 280px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  text-align: center;
  color: white;
}

.card-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.card-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 10px;
}

.card-text {
  font-size: 14px;
  opacity: 0.8;
  line-height: 1.6;
}""",
        "tags": ["card", "glass", "blur", "modern"],
    },
    {
        "name": "Hover Lift Card",
        "category": "Cards",
        "description": "Card that lifts up with shadow on hover. Smooth animation.",
        "framework": "CSS",
        "html_code": """<div class="lift-card">
  <div class="card-image"></div>
  <div class="card-content">
    <h3>Project Title</h3>
    <p>A short description of this amazing project.</p>
    <button class="card-btn">View More</button>
  </div>
</div>""",
        "css_code": """.lift-card {
  width: 300px;
  background: #1a1a2e;
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.lift-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.card-image {
  height: 180px;
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.card-content {
  padding: 20px;
  color: white;
}

.card-content h3 {
  margin-bottom: 10px;
  font-size: 20px;
}

.card-content p {
  font-size: 14px;
  opacity: 0.7;
  margin-bottom: 15px;
}

.card-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.card-btn:hover {
  background: #764ba2;
}""",
        "tags": ["card", "hover", "lift", "shadow"],
    },
    # INPUTS
    {
        "name": "Floating Label Input",
        "category": "Inputs",
        "description": "Modern input with floating label animation on focus.",
        "framework": "CSS",
        "html_code": """<div class="input-group">
  <input type="text" class="floating-input" required>
  <label class="floating-label">Email Address</label>
  <span class="highlight"></span>
</div>""",
        "css_code": """.input-group {
  position: relative;
  width: 280px;
}

.floating-input {
  width: 100%;
  padding: 14px 12px;
  font-size: 16px;
  color: #fff;
  background: transparent;
  border: 2px solid #444;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.3s;
}

.floating-input:focus {
  border-color: #667eea;
}

.floating-label {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #888;
  font-size: 16px;
  pointer-events: none;
  transition: all 0.3s ease;
  background: #0f0f0f;
  padding: 0 4px;
}

.floating-input:focus ~ .floating-label,
.floating-input:valid ~ .floating-label {
  top: 0;
  font-size: 12px;
  color: #667eea;
}""",
        "tags": ["input", "floating", "label", "form"],
    },
    {
        "name": "Underline Input",
        "category": "Inputs",
        "description": "Minimal input with animated underline on focus.",
        "framework": "CSS",
        "html_code": """<div class="underline-input-group">
  <input type="text" class="underline-input" required>
  <label>Username</label>
  <span class="underline"></span>
</div>""",
        "css_code": """.underline-input-group {
  position: relative;
  width: 280px;
  margin: 20px 0;
}

.underline-input {
  width: 100%;
  padding: 10px 0;
  font-size: 16px;
  color: #fff;
  background: transparent;
  border: none;
  border-bottom: 2px solid #444;
  outline: none;
}

.underline-input-group label {
  position: absolute;
  left: 0;
  top: 10px;
  color: #888;
  font-size: 16px;
  pointer-events: none;
  transition: all 0.3s ease;
}

.underline-input:focus ~ label,
.underline-input:valid ~ label {
  top: -16px;
  font-size: 12px;
  color: #03e9f4;
}

.underline {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: #03e9f4;
  transition: all 0.3s ease;
}

.underline-input:focus ~ .underline {
  left: 0;
  width: 100%;
}""",
        "tags": ["input", "underline", "minimal", "animated"],
    },
    # CHECKBOXES
    {
        "name": "Toggle Switch",
        "category": "Checkboxes",
        "description": "iOS-style toggle switch with smooth animation.",
        "framework": "CSS",
        "html_code": """<label class="toggle-switch">
  <input type="checkbox">
  <span class="slider"></span>
</label>""",
        "css_code": """.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: #333;
  border-radius: 34px;
  transition: 0.4s;
}

.slider::before {
  content: '';
  position: absolute;
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  border-radius: 50%;
  transition: 0.4s;
}

.toggle-switch input:checked + .slider {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.toggle-switch input:checked + .slider::before {
  transform: translateX(26px);
}""",
        "tags": ["checkbox", "toggle", "switch", "ios"],
    },
    {
        "name": "Animated Checkbox",
        "category": "Checkboxes",
        "description": "Custom checkbox with animated checkmark on select.",
        "framework": "CSS",
        "html_code": """<label class="custom-checkbox">
  <input type="checkbox">
  <span class="checkmark"></span>
  <span class="label-text">Accept terms</span>
</label>""",
        "css_code": """.custom-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 10px;
  color: #fff;
}

.custom-checkbox input {
  display: none;
}

.checkmark {
  width: 24px;
  height: 24px;
  border: 2px solid #667eea;
  border-radius: 6px;
  position: relative;
  transition: all 0.3s ease;
}

.checkmark::after {
  content: '';
  position: absolute;
  left: 7px;
  top: 3px;
  width: 6px;
  height: 12px;
  border: solid white;
  border-width: 0 3px 3px 0;
  transform: rotate(45deg) scale(0);
  transition: transform 0.2s ease;
}

.custom-checkbox input:checked + .checkmark {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: transparent;
}

.custom-checkbox input:checked + .checkmark::after {
  transform: rotate(45deg) scale(1);
}""",
        "tags": ["checkbox", "animated", "custom", "form"],
    },
    # LOADERS
    {
        "name": "Pulse Loader",
        "category": "Loaders",
        "description": "Simple pulsing circle loading animation.",
        "framework": "CSS",
        "html_code": """<div class="pulse-loader">
  <div class="pulse"></div>
  <div class="pulse"></div>
  <div class="pulse"></div>
</div>""",
        "css_code": """.pulse-loader {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pulse {
  width: 12px;
  height: 12px;
  background: #667eea;
  border-radius: 50%;
  animation: pulse 1.4s ease-in-out infinite;
}

.pulse:nth-child(1) { animation-delay: 0s; }
.pulse:nth-child(2) { animation-delay: 0.2s; }
.pulse:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}""",
        "tags": ["loader", "pulse", "animation", "loading"],
    },
]

async def add_uiverse_components():
    """Add UIverse-style components to database."""
    
    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_default_database()
    components_collection = db.components
    
    # Get user_id
    sample = await components_collection.find_one({'user_id': {'$exists': True}})
    user_id = sample.get('user_id') if sample else ObjectId("000000000000000000000001")
    
    # First, clear old incomplete components
    result = await components_collection.delete_many({'name': None})
    print(f"🗑️ Cleared {result.deleted_count} incomplete components")
    
    added_count = 0
    for comp in UIVERSE_COMPONENTS:
        # Check if already exists
        existing = await components_collection.find_one({"name": comp["name"]})
        if existing:
            print(f"⏭️ Skipping (exists): {comp['name']}")
            continue
        
        # Create component document
        component_doc = {
            "_id": ObjectId(),
            "name": comp["name"],
            "title": comp["name"],
            "category": comp["category"],
            "type": comp["category"],  # Required field
            "language": comp["framework"],  # Required field
            "difficulty_level": "Beginner",  # Required field
            "plan_type": "Free",  # Required field
            "description": comp["description"],
            "short_description": comp["description"],
            "full_description": comp["description"],  # Required field
            "developer_name": "UIverse Community",  # Required field
            "developer_experience": "5 years",  # Required field
            "framework": comp["framework"],
            "html_code": comp["html_code"],
            "css_code": comp["css_code"],
            "preview_code": f"{comp['html_code']}\n<style>\n{comp['css_code']}\n</style>",
            "code": comp["html_code"],
            "tags": comp["tags"],
            "views": 0,
            "downloads": 0,
            "likes": 0,
            "rating": 4.5,
            "is_active": True,
            "approval_status": "approved",
            "is_premium": False,
            "author": "UIverse Community",
            "author_name": "UIverse Community",
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        await components_collection.insert_one(component_doc)
        print(f"✅ Added: {comp['name']} ({comp['category']})")
        added_count += 1
    
    total = await components_collection.count_documents({})
    print(f"\n📊 Added: {added_count} components")
    print(f"📊 Total: {total} components")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_uiverse_components())
    print("\n🎉 Done!")
