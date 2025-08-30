import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.template import Template

async def test_git_url():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(database=client.user_management_db, document_models=[Template])
    
    template = await Template.get('689bd2f5a5e07fc09b45c40b')
    if template:
        print(f"Template found: {template.title}")
        print(f"Direct git_repo_url access: {template.git_repo_url}")
        
        # Test to_dict method
        template_dict = template.to_dict()
        
        # Only check git_repo_url field
        print(f"to_dict() git_repo_url: '{template_dict.get('git_repo_url', 'NOT_FOUND')}'")
        
        # Check if field exists but is None/empty
        if 'git_repo_url' in template_dict:
            value = template_dict['git_repo_url']
            print(f"git_repo_url key exists, type: {type(value)}, value: '{value}'")
            if value is None:
                print("Value is None!")
            elif value == "":
                print("Value is empty string!")
        else:
            print("git_repo_url key NOT found in dict")
    else:
        print('Template not found')

asyncio.run(test_git_url())
