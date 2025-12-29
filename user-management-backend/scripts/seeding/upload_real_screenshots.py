"""
Upload REAL website screenshots to Cloudinary and update templates.
"""
import cloudinary
import cloudinary.uploader
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

cloudinary.config(
    cloud_name="dgteyl8wn",
    api_key="923569826146345",
    api_secret="Kv19H4Sy28K2BurPvY0e-8V-OaE",
    secure=True
)

DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"
SCREENSHOTS_DIR = Path(r"C:\Users\Asus\.gemini\antigravity\brain\f2601b5c-43d4-4b55-8f7b-43624077a423")

# Real screenshots captured from websites
REAL_SCREENSHOTS = {
    "zentry_awwwards": "Awwwards Winning Website - Zentry Clone",
    "react_three_demo": "React Three Next - 3D Starter",
}

def upload_to_cloudinary(image_path: Path, public_id: str) -> str:
    print(f"📤 Uploading {image_path.name}...")
    result = cloudinary.uploader.upload(
        str(image_path),
        public_id=f"templates/{public_id}",
        folder="template_previews",
        overwrite=True,
        resource_type="image"
    )
    url = result.get("secure_url")
    print(f"✅ {url}")
    return url

async def upload_real_screenshots():
    print("=" * 60)
    print("📸 UPLOADING REAL WEBSITE SCREENSHOTS TO CLOUDINARY")
    print("=" * 60 + "\n")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    for prefix, template_title in REAL_SCREENSHOTS.items():
        # Find screenshot file
        matching_files = list(SCREENSHOTS_DIR.glob(f"{prefix}*.png"))
        
        if matching_files:
            image_path = matching_files[0]
            url = upload_to_cloudinary(image_path, prefix)
            
            # Update template
            result = await db.templates.update_one(
                {"title": template_title},
                {"$set": {"preview_images": [url]}}
            )
            
            if result.modified_count > 0:
                print(f"  ✅ Updated: {template_title}")
            else:
                print(f"  ⚠️ Not found: {template_title}")
        else:
            print(f"  ❌ No screenshot for: {prefix}")
    
    # Remove templates without previews
    print("\n🧹 Removing templates without previews...")
    result = await db.templates.delete_many({"preview_images": []})
    print(f"  Deleted {result.deleted_count} templates")
    
    # Summary
    print("\n📊 Templates with REAL previews:")
    cursor = db.templates.find({})
    count = 0
    async for t in cursor:
        title = t.get("title", "Unknown")
        has_preview = len(t.get("preview_images", [])) > 0
        if has_preview:
            count += 1
            print(f"  ✅ {title}")
    
    print(f"\nTotal: {count} templates with real screenshots")
    client.close()

if __name__ == "__main__":
    asyncio.run(upload_real_screenshots())
