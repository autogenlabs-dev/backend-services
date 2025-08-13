#!/usr/bin/env python3
"""
Update user role to admin
"""
import asyncio
from app.models import User
from app.models.user import UserRole
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import Settings

settings = Settings()

async def update_user_role():
    """Update user role to admin"""
    
    # Connect to database
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    
    # Initialize Beanie
    await init_beanie(database=db, document_models=[User])
    
    # Find the user
    user = await User.find_one({"email": "amit123@gmail.com"})
    
    if user:
        print(f"Found user: {user.email}")
        print(f"Current role: {user.role}")
        
        # Update role to admin
        user.role = UserRole.ADMIN
        await user.save()
        
        print(f"Updated role to: {user.role}")
        
        # Verify the update
        updated_user = await User.find_one({"email": "amit123@gmail.com"})
        print(f"Verified role: {updated_user.role}")
        
    else:
        print("User not found!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_user_role())
