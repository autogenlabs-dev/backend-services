import argparse
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def demote_others(except_email: str):
    client = AsyncIOMotorClient(settings.database_url)
    try:
        db = client.get_default_database()
        collection = db.get_collection('users')

        # Demote all users who do not have the except_email
        filter_query = {'email': {'$ne': except_email}}
        update = {
            '$set': {
                'role': 'user',
                'can_publish_content': False,
                'can_sell_content': False,
            }
        }
        result = await collection.update_many(filter_query, update)
        print(f'Demoted {result.modified_count} user(s) to role="user" (excluding {except_email}).')

        # Optionally, ensure the except_email is admin
        admin_result = await collection.update_one({'email': except_email}, {'$set': {'role': 'admin'}}, upsert=False)
        if admin_result.matched_count == 0:
            print(f'Warning: no user found with email {except_email}. You may want to create one first.')
        else:
            print(f'Ensured {except_email} has role=admin.')

    finally:
        client.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--except-email', required=True, help='Email to keep as admin')
    args = p.parse_args()
    asyncio.run(demote_others(args.except_email))


if __name__ == '__main__':
    main()
