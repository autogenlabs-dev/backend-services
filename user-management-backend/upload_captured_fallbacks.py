"""
Upload captured screenshots for ChadNext and Mantis.
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

CAPTURED_IMAGES = {
    "chadnext_preview": "ChadNext",
    "mantis_dashboard_preview": "Mantis Dashboard"
}

async def upload_captured():
    print("=" * 60)
    print("📸 UPLOADING CAPTURED SCREENSHOTS")
    print("=" * 60 + "\n")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    for prefix, title in CAPTURED_IMAGES.items():
        matching_files = list(SCREENSHOTS_DIR.glob(f"{prefix}*.png"))
        if matching_files:
            image_path = matching_files[0]
            print(f"📤 Uploading {image_path.name}...")
            
            result = cloudinary.uploader.upload(
                str(image_path),
                public_id=f"templates/{prefix}",
                folder="template_previews",
                overwrite=True,
                resource_type="image"
            )
            url = result.get("secure_url")
            
            await db.templates.update_one(
                {"title": title},
                {"$set": {"preview_images": [url]}}
            )
            print(f"   ✅ Updated {title}: {url}")
        else:
            print(f"   ❌ No screenshot found for {title}")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(upload_captured())
