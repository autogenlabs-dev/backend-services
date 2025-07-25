#!/usr/bin/env python3
"""
Get the OpenAPI spec to see available endpoints
"""
import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"

async def get_openapi_spec():
    """Get OpenAPI specification"""
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/openapi.json") as response:
                if response.status == 200:
                    spec = await response.json()
                    
                    print("🔍 Available API Endpoints:")
                    print("=" * 50)
                    
                    paths = spec.get("paths", {})
                    for path, methods in paths.items():
                        for method, details in methods.items():
                            summary = details.get("summary", "No description")
                            tags = details.get("tags", [])
                            print(f"📍 {method.upper()} {path}")
                            print(f"   📝 {summary}")
                            if tags:
                                print(f"   🏷️ Tags: {', '.join(tags)}")
                            print()
                            
                else:
                    print(f"❌ Failed to get OpenAPI spec: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error getting OpenAPI spec: {e}")

if __name__ == "__main__":
    asyncio.run(get_openapi_spec())
