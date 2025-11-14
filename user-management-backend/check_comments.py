import asyncio
from app.models.component_interactions import ComponentComment
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

async def check_comments():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(database=client.user_management_db, document_models=[ComponentComment])
    
    comments = await ComponentComment.find().to_list()
    print(f'Total comments: {len(comments)}')
    
    for c in comments[-5:]:  # Last 5 comments
        print(f'Comment: {c.id} - component_id: {c.component_id} ({type(c.component_id)}) - content: {c.comment}')
    
    # Check specific component
    target_component = "6898e97ba4f90603e5afe1e9"
    specific_comments = await ComponentComment.find({"component_id": target_component}).to_list()
    print(f'\nComments for component {target_component}: {len(specific_comments)}')
    
    # Try with ObjectId
    from beanie import PydanticObjectId
    try:
        oid_comments = await ComponentComment.find({"component_id": PydanticObjectId(target_component)}).to_list()
        print(f'Comments with ObjectId: {len(oid_comments)}')
    except Exception as e:
        print(f'ObjectId query failed: {e}')

if __name__ == "__main__":
    asyncio.run(check_comments())
