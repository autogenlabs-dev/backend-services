"""Remove templates without previews."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def remove_no_preview():
    client = AsyncIOMotorClient("mongodb://admin:password123@localhost:27017/user_management_db?authSource=admin")
    db = client.user_management_db
    
    # Delete templates without previews
    result = await db.templates.delete_many({"preview_images": []})
    print(f"Deleted {result.deleted_count} templates without previews")
    
    # Show remaining
    cursor = db.templates.find({})
    print("Remaining templates:")
    async for t in cursor:
        title = t.get("title", "Unknown")
        print(f"  - {title}")
    
    count = await db.templates.count_documents({})
    print(f"Total: {count} templates")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(remove_no_preview())
