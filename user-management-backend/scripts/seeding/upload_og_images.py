"""
Fetch Open Graph images from websites and upload to Cloudinary.
Update templates with these verified preview images.
"""
import requests
from bs4 import BeautifulSoup
import cloudinary
import cloudinary.uploader
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Cloudinary Config
cloudinary.config(
    cloud_name="dgteyl8wn",
    api_key="923569826146345",
    api_secret="Kv19H4Sy28K2BurPvY0e-8V-OaE",
    secure=True
)

DATABASE_URL = "mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin"

# Map of template titles to their live URLs
TEMPLATE_URLS = {
    "Horizon UI": "https://horizon-ui.com/chakra",
    "Typebot": "https://typebot.io",
    "Formbricks": "https://formbricks.com",
    "Twenty": "https://twenty.com",
    "Plane": "https://plane.so",
    "Infisical": "https://infisical.com",
    "Dub.co": "https://dub.co",
    "Flowise": "https://flowiseai.com",
    "Novel": "https://novel.sh",
    "Vercel Commerce": "https://demo.vercel.store",
    # Also retry the ones that might have failed or need better images
    "ChadNext": "https://chadnext.moinulmoin.com",
    "Mantis Dashboard": "https://mantisdashboard.io/free",
    "Precedent": "https://precedent.dev",
    "RoomGPT": "https://roomgpt.io",
    "Skateshop": "https://skateshop.sadmn.com"
}

def get_og_image(url):
    try:
        print(f"🔍 Fetching OG image for {url}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            # Handle relative URLs
            if img_url.startswith('/'):
                from urllib.parse import urljoin
                img_url = urljoin(url, img_url)
            print(f"   Found: {img_url}")
            return img_url
        else:
            print("   ❌ No OG image found")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def upload_to_cloudinary(img_url, public_id):
    try:
        print(f"📤 Uploading to Cloudinary...")
        result = cloudinary.uploader.upload(
            img_url,
            public_id=f"templates/{public_id}",
            folder="template_previews",
            overwrite=True,
            resource_type="image"
        )
        url = result.get("secure_url")
        print(f"   ✅ Uploaded: {url}")
        return url
    except Exception as e:
        print(f"   ❌ Upload Error: {e}")
        return None

async def process_templates():
    print("=" * 60)
    print("🖼️ FETCHING AND UPLOADING PREVIEW IMAGES")
    print("=" * 60 + "\n")
    
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.user_management_db
    
    for title, url in TEMPLATE_URLS.items():
        print(f"\nProcessing: {title}")
        
        # 1. Get OG Image
        og_url = get_og_image(url)
        
        if og_url:
            # 2. Upload to Cloudinary
            safe_id = title.lower().replace(" ", "_").replace(".", "")
            cloudinary_url = upload_to_cloudinary(og_url, safe_id)
            
            if cloudinary_url:
                # 3. Update Database
                await db.templates.update_one(
                    {"title": title},
                    {"$set": {"preview_images": [cloudinary_url]}}
                )
                print(f"   💾 Database updated")
            else:
                print("   ⚠️ Skipping DB update (upload failed)")
        else:
            print("   ⚠️ Skipping (no image found)")
            
    # Final Summary
    print("\n" + "=" * 60)
    print("FINAL STATUS")
    print("=" * 60)
    
    cursor = db.templates.find({})
    count = 0
    async for t in cursor:
        title = t.get("title", "Unknown")
        has_preview = len(t.get("preview_images", [])) > 0
        status = "✅" if has_preview else "❌"
        if has_preview: count += 1
        print(f"{status} {title}")
        
    print(f"\nTotal with previews: {count}")
    client.close()

if __name__ == "__main__":
    asyncio.run(process_templates())
