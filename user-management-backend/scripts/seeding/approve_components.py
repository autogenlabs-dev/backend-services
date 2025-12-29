import asyncio
import logging
import os
import sys

# Add current directory to path to allow imports from app
sys.path.append(os.getcwd())

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.component import Component, ContentStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def approve_all_components():
    logger.info("🔄 Connecting to database...")
    # Ensure we use the correct database URL
    logger.info(f"   Database URL: {settings.database_url}")
    
    client = AsyncIOMotorClient(settings.database_url)
    database = client["user_management_db"]
    
    logger.info("🔄 Initializing Beanie...")
    await init_beanie(database=database, document_models=[Component])
    
    logger.info("🔍 Finding all components...")
    components = await Component.find_all().to_list()
    logger.info(f"📊 Found {len(components)} components.")
    
    count = 0
    for component in components:
        # Update if not already approved or if we want to force update
        if component.approval_status != ContentStatus.APPROVED:
            component.approval_status = ContentStatus.APPROVED
            # Ensure is_active is also true
            component.is_active = True
            await component.save()
            count += 1
            logger.info(f"✅ Approved component: {component.title} ({component.id})")
        else:
            # Ensure is_active is true even if already approved
            if not component.is_active:
                component.is_active = True
                await component.save()
                count += 1
                logger.info(f"✅ Activated component: {component.title} ({component.id})")
    
    logger.info(f"🎉 Finished! Updated {count} components.")

if __name__ == "__main__":
    asyncio.run(approve_all_components())
