"""
Upload new generated preview images to Cloudinary and update templates.
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

DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"
SCREENSHOTS_DIR = Path(r"C:\Users\Asus\.gemini\antigravity\brain\f2601b5c-43d4-4b55-8f7b-43624077a423")

# New templates and their generated images
NEW_TEMPLATE_IMAGES = {
    "taxonomy_landing_preview": "Taxonomy Landing Page",
    "spotlight_portfolio_preview": "Spotlight Portfolio",
}

def upload_to_cloudinary(image_path: Path, public_id: str) -> str:
    """Upload image to Cloudinary and return URL."""
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

async def upload_new_previews():
    print("=" * 60)
    print("UPLOADING NEW PREVIEW IMAGES TO CLOUDINARY")
    print("=" * 60 + "\n")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    # Find and upload new images
    for prefix, template_title in NEW_TEMPLATE_IMAGES.items():
        # Find the image file
        matching_files = list(SCREENSHOTS_DIR.glob(f"{prefix}*.png"))
        
        if matching_files:
            image_path = matching_files[0]
            url = upload_to_cloudinary(image_path, prefix)
            
            # Update template in database
            result = await db.templates.update_one(
                {"title": template_title},
                {"$set": {"preview_images": [url]}}
            )
            
            if result.modified_count > 0:
                print(f"  Updated: {template_title}")
            else:
                print(f"  Not found: {template_title}")
        else:
            print(f"  No image found for: {prefix}")
    
    # Show summary
    print("\n" + "=" * 60)
    print("TEMPLATE STATUS")
    print("=" * 60)
    
    cursor = db.templates.find({})
    async for t in cursor:
        title = t.get("title", "Unknown")
        has_preview = len(t.get("preview_images", [])) > 0
        status = "✅" if has_preview else "❌"
        print(f"  {status} {title}")
    
    client.close()
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(upload_new_previews())
