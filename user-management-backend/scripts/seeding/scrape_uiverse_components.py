"""
UIverse.io Component Scraper
Scrapes best UI components from uiverse.io and uploads them to MongoDB.
Components are MIT licensed open-source UI elements.
"""

import asyncio
import re
from datetime import datetime, timezone
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
MONGODB_URL = "mongodb://admin:password123@51.20.108.69:27017/user_management_db?authSource=admin"
COMPONENTS_PER_CATEGORY = 10  # Top 10 from each category

# UIverse categories with URL slugs
CATEGORIES = [
    {"name": "Buttons", "slug": "buttons"},
    {"name": "Cards", "slug": "cards"},
    {"name": "Loaders", "slug": "loaders"},
    {"name": "Toggle Switches", "slug": "toggle-switches"},
    {"name": "Inputs", "slug": "inputs"},
    {"name": "Checkboxes", "slug": "checkboxes"},
    {"name": "Patterns", "slug": "patterns"},
    {"name": "Forms", "slug": "forms"},
    {"name": "Radio Buttons", "slug": "radio-buttons"},
    {"name": "Tooltips", "slug": "tooltips"},
]


async def scrape_component_details(page, component_url: str) -> Optional[dict]:
    """Scrape details from a single component page."""
    try:
        await page.goto(component_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1000)  # Wait for dynamic content
        
        # Extract component name
        name_el = await page.query_selector("h1, .element-title, [class*='title']")
        name = await name_el.inner_text() if name_el else "Unnamed Component"
        name = name.strip()
        
        # Extract author
        author_el = await page.query_selector("a[href*='/profile/'], [class*='author'], [class*='creator']")
        author = await author_el.inner_text() if author_el else "UIverse Community"
        author = author.strip()
        
        # Extract likes count
        likes_el = await page.query_selector("[class*='like'] span, [class*='heart'] + span, button[class*='like'] span")
        likes_text = await likes_el.inner_text() if likes_el else "0"
        likes = int(re.sub(r'[^\d]', '', likes_text) or 0)
        
        # Click on "Get Code" or code tab if available
        code_btn = await page.query_selector("button:has-text('Get Code'), button:has-text('Code'), [class*='code-tab']")
        if code_btn:
            await code_btn.click()
            await page.wait_for_timeout(500)
        
        # Extract HTML code
        html_code = ""
        html_el = await page.query_selector("pre:has-text('<'), [class*='html'] pre, [class*='html'] code, textarea[placeholder*='HTML']")
        if html_el:
            html_code = await html_el.inner_text()
        
        # Try alternative: look for copy buttons and associated code blocks
        if not html_code:
            code_blocks = await page.query_selector_all("pre, code")
            for block in code_blocks:
                text = await block.inner_text()
                if '<' in text and '>' in text and not text.strip().startswith('.') and not text.strip().startswith('{'):
                    html_code = text
                    break
        
        # Extract CSS code
        css_code = ""
        css_el = await page.query_selector("[class*='css'] pre, [class*='css'] code, pre:has-text('.'), textarea[placeholder*='CSS']")
        if css_el:
            css_code = await css_el.inner_text()
        
        # Try alternative for CSS
        if not css_code:
            code_blocks = await page.query_selector_all("pre, code")
            for block in code_blocks:
                text = await block.inner_text()
                if (text.strip().startswith('.') or text.strip().startswith('@') or '{' in text) and '<' not in text:
                    css_code = text
                    break
        
        # Skip if no code found
        if not html_code and not css_code:
            print(f"    ⚠️ No code found, skipping...")
            return None
        
        # Extract description/tags if available
        desc_el = await page.query_selector("[class*='description'], [class*='desc'], p.text-gray")
        description = await desc_el.inner_text() if desc_el else f"Beautiful {name} component from UIverse"
        
        # Extract tags
        tags = []
        tag_els = await page.query_selector_all("[class*='tag'], [class*='badge'], .chip")
        for tag_el in tag_els[:5]:  # Max 5 tags
            tag_text = await tag_el.inner_text()
            if tag_text and len(tag_text) < 20:
                tags.append(tag_text.lower().strip())
        
        return {
            "name": name,
            "author": author,
            "likes": likes,
            "html_code": html_code.strip(),
            "css_code": css_code.strip(),
            "description": description.strip(),
            "tags": tags,
            "source_url": component_url,
        }
        
    except PlaywrightTimeout:
        print(f"    ⏱️ Timeout loading component")
        return None
    except Exception as e:
        print(f"    ❌ Error: {str(e)[:50]}")
        return None


async def scrape_category(page, category: dict) -> list:
    """Scrape top components from a category page."""
    components = []
    category_url = f"https://uiverse.io/{category['slug']}?sort=likes"  # Sort by most liked
    
    print(f"\n📂 Scraping {category['name']}...")
    
    try:
        await page.goto(category_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)  # Wait for components to load
        
        # Find component cards/links
        component_links = await page.query_selector_all("a[href*='/element/'], a[href*='/u/'], .element-card a, [class*='card'] a")
        
        # Get unique component URLs
        urls = set()
        for link in component_links:
            href = await link.get_attribute("href")
            if href and ("/element/" in href or "/u/" in href):
                if not href.startswith("http"):
                    href = f"https://uiverse.io{href}"
                urls.add(href)
        
        urls = list(urls)[:COMPONENTS_PER_CATEGORY]
        print(f"  Found {len(urls)} components to scrape")
        
        for i, url in enumerate(urls):
            print(f"  [{i+1}/{len(urls)}] {url.split('/')[-1][:30]}...")
            component = await scrape_component_details(page, url)
            if component:
                component["category"] = category["name"]
                components.append(component)
                print(f"    ✅ {component['name'][:40]}")
        
    except PlaywrightTimeout:
        print(f"  ⏱️ Timeout loading category page")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    return components


async def upload_to_mongodb(components: list, dry_run: bool = False):
    """Upload scraped components to MongoDB."""
    if dry_run:
        print(f"\n🔍 DRY RUN - Would upload {len(components)} components:")
        for comp in components:
            print(f"  - {comp['name']} ({comp['category']})")
        return
    
    print(f"\n🔌 Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.user_management_db
    collection = db.components
    
    # Get or create system user_id
    user = await db.users.find_one({})
    user_id = user["_id"] if user else ObjectId("000000000000000000000001")
    
    added = 0
    skipped = 0
    
    for comp in components:
        # Check if already exists
        existing = await collection.find_one({"source_url": comp["source_url"]})
        if existing:
            print(f"  ⏭️ Exists: {comp['name'][:40]}")
            skipped += 1
            continue
        
        # Create component document
        doc = {
            "_id": ObjectId(),
            "name": comp["name"],
            "title": comp["name"],
            "category": comp["category"],
            "type": comp["category"],
            "language": "CSS",
            "difficulty_level": "Beginner",
            "plan_type": "Free",
            "short_description": comp["description"][:200] if comp["description"] else f"{comp['category']} component",
            "full_description": comp["description"],
            "developer_name": comp["author"],
            "developer_experience": "Community",
            "html_code": comp["html_code"],
            "css_code": comp["css_code"],
            "preview_code": f"{comp['html_code']}\n<style>\n{comp['css_code']}\n</style>",
            "code": comp["html_code"],
            "tags": comp["tags"] + [comp["category"].lower()],
            "views": 0,
            "downloads": 0,
            "likes": comp["likes"],
            "rating": 4.5,
            "is_active": True,
            "approval_status": "approved",
            "is_premium": False,
            "source_url": comp["source_url"],
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        await collection.insert_one(doc)
        print(f"  ✅ Added: {comp['name'][:40]}")
        added += 1
    
    total = await collection.count_documents({})
    print(f"\n📊 Summary:")
    print(f"  Added: {added}")
    print(f"  Skipped: {skipped}")
    print(f"  Total in DB: {total}")
    
    client.close()


async def main(dry_run: bool = False):
    """Main scraper function."""
    print("=" * 60)
    print("🎨 UIverse.io Component Scraper")
    print("=" * 60)
    print(f"Categories to scrape: {len(CATEGORIES)}")
    print(f"Components per category: {COMPONENTS_PER_CATEGORY}")
    print(f"Target: ~{len(CATEGORIES) * COMPONENTS_PER_CATEGORY} components")
    
    all_components = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for category in CATEGORIES:
            components = await scrape_category(page, category)
            all_components.extend(components)
            await page.wait_for_timeout(1000)  # Rate limiting
        
        await browser.close()
    
    print(f"\n✅ Total scraped: {len(all_components)} components")
    
    # Upload to MongoDB
    await upload_to_mongodb(all_components, dry_run=dry_run)
    
    print("\n🎉 Done!")


if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("🔍 Running in DRY RUN mode - no database changes")
    asyncio.run(main(dry_run=dry_run))
