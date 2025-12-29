"""
Script to validate template URLs and clean up database.
Tests each template's live_demo_url to ensure the website is accessible.
Removes templates with broken/inaccessible URLs.
"""

import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import ssl

# Load .env file
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/user_management_db")

# Timeout for URL checks (seconds)
TIMEOUT = 15

async def check_url(session, url, template_title):
    """Check if a URL is accessible."""
    try:
        # Skip invalid URLs
        if not url or not url.startswith(('http://', 'https://')):
            print(f"  ❌ {template_title}: Invalid URL format")
            return False, "Invalid URL format"
        
        # Create SSL context that doesn't verify certificates (some sites have issues)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT), 
                               ssl=ssl_context, allow_redirects=True) as response:
            if response.status == 200:
                print(f"  ✅ {template_title}: {url} - OK ({response.status})")
                return True, None
            elif response.status in [301, 302, 303, 307, 308]:
                print(f"  ✅ {template_title}: {url} - Redirect ({response.status})")
                return True, None
            elif response.status == 403:
                # Some sites return 403 but are still accessible
                print(f"  ⚠️ {template_title}: {url} - Forbidden ({response.status}) - keeping")
                return True, None
            else:
                print(f"  ❌ {template_title}: {url} - Error ({response.status})")
                return False, f"HTTP {response.status}"
    except asyncio.TimeoutError:
        print(f"  ❌ {template_title}: {url} - Timeout")
        return False, "Timeout"
    except aiohttp.ClientConnectorError as e:
        print(f"  ❌ {template_title}: {url} - Connection error")
        return False, "Connection error"
    except Exception as e:
        print(f"  ❌ {template_title}: {url} - Error: {str(e)[:50]}")
        return False, str(e)[:50]

async def validate_and_clean_templates():
    """Test all template URLs and remove broken ones."""
    
    print("🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.get_default_database()
    templates_collection = db.templates
    
    # Get all templates
    templates = await templates_collection.find({}).to_list(1000)
    print(f"📊 Total templates to check: {len(templates)}")
    
    # Track results
    valid_templates = []
    invalid_templates = []
    
    # Create aiohttp session
    connector = aiohttp.TCPConnector(limit=10)  # Limit concurrent connections
    async with aiohttp.ClientSession(connector=connector) as session:
        print("\n🔍 Testing template URLs...")
        
        for template in templates:
            url = template.get('live_demo_url')
            title = template.get('title', 'Unknown')
            template_id = template.get('_id')
            
            if url:
                is_valid, error = await check_url(session, url, title)
                if is_valid:
                    valid_templates.append(template_id)
                else:
                    invalid_templates.append({
                        'id': template_id,
                        'title': title,
                        'url': url,
                        'error': error
                    })
            else:
                print(f"  ❌ {title}: No URL provided")
                invalid_templates.append({
                    'id': template_id,
                    'title': title,
                    'url': None,
                    'error': "No URL"
                })
    
    # Print summary
    print(f"\n📊 Results Summary:")
    print(f"  ✅ Valid templates: {len(valid_templates)}")
    print(f"  ❌ Invalid templates: {len(invalid_templates)}")
    
    # List invalid templates
    if invalid_templates:
        print(f"\n❌ Templates to be removed:")
        for t in invalid_templates:
            print(f"  - {t['title']}: {t['url']} ({t['error']})")
    
    # Delete invalid templates
    if invalid_templates:
        print(f"\n🗑️ Deleting {len(invalid_templates)} invalid templates...")
        invalid_ids = [t['id'] for t in invalid_templates]
        result = await templates_collection.delete_many({'_id': {'$in': invalid_ids}})
        print(f"  Deleted: {result.deleted_count} templates")
    
    # Final count
    remaining = await templates_collection.count_documents({})
    print(f"\n📊 Final template count: {remaining}")
    
    # List remaining templates
    print(f"\n✅ Remaining valid templates:")
    valid_list = await templates_collection.find({}).to_list(100)
    for t in valid_list:
        print(f"  - {t.get('title')}: {t.get('live_demo_url')}")
    
    client.close()
    return len(valid_templates), len(invalid_templates)

if __name__ == "__main__":
    valid, invalid = asyncio.run(validate_and_clean_templates())
    print(f"\n🎉 Done! {valid} valid, {invalid} removed")
