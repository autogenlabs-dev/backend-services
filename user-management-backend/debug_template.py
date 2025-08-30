import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.template import Template

async def check_template():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(database=client.user_management_db, document_models=[Template])
    
    template = await Template.get('689bd2f5a5e07fc09b45c40b')
    if template:
        print('Template found:')
        print(f'Title: {template.title}')
        print(f'Git URL in raw field: {getattr(template, "git_repo_url", "NOT_FOUND")}')
        print('Raw document dict:')
        raw_dict = template.dict()
        print(f'Git URL in dict: {raw_dict.get("git_repo_url", "NOT_FOUND")}')
        print('Using to_dict method:')
        api_dict = template.to_dict()
        print(f'Git URL in to_dict: {api_dict.get("git_repo_url", "NOT_FOUND")}')
        
        # Check all fields
        print('\nAll fields in raw dict:')
        for key, value in raw_dict.items():
            if 'git' in key.lower() or 'url' in key.lower():
                print(f'{key}: {value}')
    else:
        print('Template not found')

asyncio.run(check_template())
