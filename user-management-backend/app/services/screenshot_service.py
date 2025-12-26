"""
Screenshot service for capturing website previews.
Uses Playwright to capture screenshots of websites.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, JSONResponse
import asyncio
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Cache directory for screenshots
CACHE_DIR = Path("/tmp/screenshots")
CACHE_DIR.mkdir(exist_ok=True)

# In-memory cache for screenshot URLs
screenshot_cache = {}

async def capture_screenshot(url: str, width: int = 1280, height: int = 720) -> bytes:
    """
    Capture a screenshot of a website using Playwright.
    Falls back to a placeholder if Playwright is not available.
    """
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": width, "height": height})
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(1)  # Wait for any animations
                screenshot = await page.screenshot(type="png")
                return screenshot
            except Exception as e:
                logger.error(f"Failed to capture {url}: {e}")
                raise
            finally:
                await browser.close()
                
    except ImportError:
        logger.warning("Playwright not installed. Using placeholder.")
        # Generate a placeholder image
        return generate_placeholder_image(url, width, height)

def generate_placeholder_image(url: str, width: int, height: int) -> bytes:
    """Generate a simple placeholder image with the URL text."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create gradient background
        img = Image.new('RGB', (width, height), color=(20, 20, 30))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient-like effect
        for y in range(height):
            color_value = int(20 + (y / height) * 30)
            draw.line([(0, y), (width, y)], fill=(color_value, color_value, color_value + 10))
        
        # Draw URL text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Extract domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc or url[:50]
        
        # Center the text
        text = f"Preview: {domain}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(100, 200, 255), font=font)
        
        # Save to bytes
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
        
    except ImportError:
        # If PIL is not available, return a minimal PNG
        logger.warning("PIL not installed. Returning minimal placeholder.")
        # Minimal 1x1 PNG
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'

def get_cache_path(url: str) -> Path:
    """Get the cache file path for a URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{url_hash}.png"

@router.get("/screenshot")
async def get_screenshot(
    url: str = Query(..., description="URL of the website to screenshot"),
    width: int = Query(1280, description="Screenshot width"),
    height: int = Query(720, description="Screenshot height"),
    format: str = Query("image", description="Response format: 'image' or 'url'")
):
    """
    Capture a screenshot of a website.
    
    - **url**: The website URL to capture
    - **width**: Screenshot width (default: 1280)
    - **height**: Screenshot height (default: 720)
    - **format**: Response format - 'image' returns PNG, 'url' returns JSON with data URL
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Check cache
    cache_path = get_cache_path(url)
    
    if cache_path.exists():
        # Return cached screenshot
        with open(cache_path, 'rb') as f:
            screenshot_data = f.read()
    else:
        # Capture new screenshot
        try:
            screenshot_data = await capture_screenshot(url, width, height)
            
            # Save to cache
            with open(cache_path, 'wb') as f:
                f.write(screenshot_data)
                
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            # Generate placeholder on error
            screenshot_data = generate_placeholder_image(url, width, height)
    
    if format == "url":
        import base64
        data_url = f"data:image/png;base64,{base64.b64encode(screenshot_data).decode()}"
        return JSONResponse({
            "success": True,
            "screenshot_url": data_url,
            "url": url,
            "width": width,
            "height": height
        })
    else:
        return Response(
            content=screenshot_data,
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=86400",
                "X-Screenshot-URL": url
            }
        )

@router.get("/screenshot/clear-cache")
async def clear_screenshot_cache():
    """Clear the screenshot cache."""
    count = 0
    for file in CACHE_DIR.glob("*.png"):
        file.unlink()
        count += 1
    
    return {"success": True, "cleared": count}
