"""Direct database test for component creation without API layer."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, PydanticObjectId
from datetime import datetime, timezone
import os

# Import models
import sys
sys.path.insert(0, '/app')
from app.models.component import Component

async def test_component_creation():
    """Test component creation directly against MongoDB."""
    print("🔌 Connecting to MongoDB...")
    
    # Get MongoDB URL from environment or use default
    mongo_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    print(f"   MongoDB URL: {mongo_url}")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    database = client.codemurf
    
    print("🔧 Initializing Beanie...")
    await init_beanie(database=database, document_models=[Component])
    
    print("\n📊 Current component count:")
    count_before = await Component.find_all().count()
    print(f"   Components in database: {count_before}")
    
    print("\n🔨 Creating test component...")
    test_component = Component(
        title="Test Button Component",
        category="User Interface",
        type="button",
        language="HTML/Tailwind",
        difficulty_level="Beginner",
        plan_type="Free",
        short_description="A test button component",
        full_description="This is a test button component created for debugging",
        preview_images=[],
        git_repo_url=None,
        live_demo_url=None,
        dependencies=[],
        tags=["test", "button"],
        developer_name="Test Developer",
        developer_experience="Junior",
        is_available_for_dev=True,
        featured=False,
        code='<button class="px-6 py-3 bg-blue-500">Test Button</button>',
        readme_content=None,
        user_id=PydanticObjectId("507f1f77bcf86cd799439011"),  # Dummy user ID for testing
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    print(f"   Component title: {test_component.title}")
    print(f"   Component ID before insert: {test_component.id}")
    
    print("\n💾 Inserting component...")
    await test_component.insert()
    
    print(f"   Component ID after insert: {test_component.id}")
    
    if not test_component.id:
        print("❌ ERROR: Component ID is None after insert!")
        return False
    
    print("\n🔍 Verifying component in database...")
    retrieved = await Component.get(test_component.id)
    
    if not retrieved:
        print(f"❌ ERROR: Component {test_component.id} not found in database!")
        return False
    
    print(f"✅ Component found!")
    print(f"   ID: {retrieved.id}")
    print(f"   Title: {retrieved.title}")
    print(f"   Category: {retrieved.category}")
    
    print("\n📊 Final component count:")
    count_after = await Component.find_all().count()
    print(f"   Components in database: {count_after}")
    print(f"   New components created: {count_after - count_before}")
    
    print("\n🧹 Cleaning up test component...")
    await test_component.delete()
    
    count_final = await Component.find_all().count()
    print(f"   Components after cleanup: {count_final}")
    
    print("\n✅ Test completed successfully!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_component_creation())
    exit(0 if success else 1)
