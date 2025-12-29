"""Test script to check and provision OpenRouter keys for users."""

import asyncio
import sys
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Check user's OpenRouter key status and provision if needed."""
    from app.config import settings
    from app.models.user import User
    from app.services.openrouter_keys import ensure_user_openrouter_key, refresh_user_openrouter_key
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.database_url)
    # Extract database name from connection string
    db_name = settings.database_url.split('/')[-1].split('?')[0]
    db = client[db_name]
    
    # Initialize Beanie
    await init_beanie(database=db, document_models=[User])
    
    # Get email from command line or use a test email
    email = sys.argv[1] if len(sys.argv) > 1 else None
    
    if email:
        user = await User.find_one(User.email == email)
        if not user:
            logger.error(f"User with email {email} not found")
            return
    else:
        # Get the first user
        user = await User.find_one()
        if not user:
            logger.error("No users found in database")
            return
    
    logger.info(f"Checking user: {user.email}")
    logger.info(f"User ID: {user.id}")
    logger.info(f"Current openrouter_api_key: {user.openrouter_api_key[:30] if user.openrouter_api_key else 'None'}...")
    logger.info(f"Has openrouter_api_key_hash: {bool(user.openrouter_api_key_hash)}")
    
    # Check provisioning key
    if not settings.openrouter_provisioning_api_key:
        logger.error("OPENROUTER_PROVISIONING_API_KEY is not set!")
        return
    
    logger.info(f"Provisioning key is set: {settings.openrouter_provisioning_api_key[:20]}...")
    
    # Test provisioning
    try:
        logger.info("Attempting to provision/refresh OpenRouter key...")
        key_value = await refresh_user_openrouter_key(user)
        logger.info(f"✓ Successfully provisioned key: {key_value[:30]}...")
        
        # Reload user to verify
        user = await User.get(user.id)
        logger.info(f"✓ User's openrouter_api_key after refresh: {user.openrouter_api_key[:30] if user.openrouter_api_key else 'None'}...")
        
    except Exception as e:
        logger.error(f"✗ Failed to provision key: {e}", exc_info=True)
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
