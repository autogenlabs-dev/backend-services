"""
Script to capture real website screenshots using Playwright
and store them as base64 or serve them locally.
"""

import asyncio
from playwright.async_api import async_playwright
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import base64
from pathlib import Path

# Load .env file
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/user_management_db")

# Screenshot output directory
SCREENSHOTS_DIR = Path("/home/cis/Music/Autogenlabs-Web-App/public/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

async def capture_screenshot(page, url, filename):
    """Capture a screenshot of a website."""
    try:
        print(f"  📸 Capturing: {url}")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)  # Wait for animations
        
        screenshot_path = SCREENSHOTS_DIR / filename
        await page.screenshot(path=str(screenshot_path), full_page=False)
        
        print(f"  ✅ Saved: {filename}")
        return f"/screenshots/{filename}"
    except Exception as e:
        print(f"  ❌ Failed: {url} - {str(e)[:50]}")
        return None

async def generate_all_screenshots():
    """Generate screenshots for all templates."""
    
    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_default_database()
    templates_collection = db.templates
    
    # Get all templates
    templates = await templates_collection.find({}).to_list(100)
    print(f"📊 Templates to capture: {len(templates)}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=1
        )
        page = await context.new_page()
        
        for template in templates:
            url = template.get('live_demo_url')
            title = template.get('title', 'unknown')
            template_id = str(template.get('_id'))
            
            if url:
                # Create safe filename
                safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in title[:30])
                filename = f"{template_id}_{safe_name}.png"
                
                screenshot_url = await capture_screenshot(page, url, filename)
                
                if screenshot_url:
                    # Update template with preview image
                    await templates_collection.update_one(
                        {'_id': template['_id']},
                        {'$set': {'preview_images': [screenshot_url]}}
                    )
                    print(f"  ✅ Updated template: {title}")
        
        await browser.close()
    
    # Verify
    print(f"\n📊 Screenshots saved to: {SCREENSHOTS_DIR}")
    print(f"📁 Files created: {len(list(SCREENSHOTS_DIR.glob('*.png')))}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(generate_all_screenshots())
    print("\n🎉 Done! Screenshots generated and database updated.")
