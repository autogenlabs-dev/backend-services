"""
Upload template screenshots to Cloudinary and update templates with preview URLs.
"""
import cloudinary
import cloudinary.uploader
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

# Cloudinary Configuration
cloudinary.config(
    cloud_name="dgteyl8wn",
    api_key="923569826146345",
    api_secret="Kv19H4Sy28K2BurPvY0e-8V-OaE",
    secure=True
)

# MongoDB connection
DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

# Screenshots directory
SCREENSHOTS_DIR = Path(r"C:\Users\Asus\.gemini\antigravity\brain\f2601b5c-43d4-4b55-8f7b-43624077a423")

# Mapping of screenshot files to template titles
SCREENSHOT_MAPPING = {
    "developer_portfolio": "Developer Portfolio - Next.js",
    "open_cruip": "Open React Landing Page",
    "next_saas_starter": "Next.js SaaS Starter",
    "tailwind_blog": "Tailwind Blog Starter",
    "mosaic_dashboard": "Mosaic Dashboard",
}

def upload_to_cloudinary(image_path: Path, public_id: str) -> str:
    """Upload image to Cloudinary and return URL."""
    print(f"📤 Uploading {image_path.name} to Cloudinary...")
    
    result = cloudinary.uploader.upload(
        str(image_path),
        public_id=f"templates/{public_id}",
        folder="template_previews",
        overwrite=True,
        resource_type="image"
    )
    
    url = result.get("secure_url")
    print(f"✅ Uploaded: {url}")
    return url

async def update_templates_with_previews():
    """Upload screenshots and update templates with preview URLs."""
    print("=" * 60)
    print("📸 UPLOADING SCREENSHOTS TO CLOUDINARY")
    print("=" * 60 + "\n")
    
    # Find all screenshot files
    screenshots = list(SCREENSHOTS_DIR.glob("*.png"))
    print(f"Found {len(screenshots)} screenshots\n")
    
    # Upload each screenshot and collect URLs
    uploaded_urls = {}
    
    for screenshot in screenshots:
        # Find matching template name
        for key, template_title in SCREENSHOT_MAPPING.items():
            if key in screenshot.name:
                url = upload_to_cloudinary(screenshot, key)
                uploaded_urls[template_title] = url
                break
    
    print(f"\n✅ Uploaded {len(uploaded_urls)} screenshots to Cloudinary\n")
    
    # Update templates in MongoDB
    print("🔄 Updating templates with preview URLs...")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    updated_count = 0
    for title, url in uploaded_urls.items():
        result = await db.templates.update_one(
            {"title": title},
            {"$set": {"preview_images": [url]}}
        )
        if result.modified_count > 0:
            print(f"  ✅ Updated: {title}")
            updated_count += 1
        else:
            # Try partial match
            result = await db.templates.update_one(
                {"title": {"$regex": title.split(" - ")[0], "$options": "i"}},
                {"$set": {"preview_images": [url]}}
            )
            if result.modified_count > 0:
                print(f"  ✅ Updated (partial match): {title}")
                updated_count += 1
    
    print(f"\n✅ Updated {updated_count} templates with preview URLs!")
    
    # Show summary
    print("\n📊 Templates with previews:")
    cursor = db.templates.find({"preview_images": {"$ne": []}})
    async for template in cursor:
        print(f"  - {template['title']}: {template['preview_images'][0][:60]}...")
    
    client.close()
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(update_templates_with_previews())
