import argparse
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def make_user_admin(email: str, publish: bool = False, sell: bool = False):
    client = AsyncIOMotorClient(settings.database_url)
    try:
        db = client.get_default_database()

        # collection name is 'users' per app/models/user.py
        collection = db.get_collection('users')

        update = {'role': 'admin'}
        if publish:
            update['can_publish_content'] = True
        if sell:
            update['can_sell_content'] = True

        result = await collection.update_one({'email': email}, {'$set': update}, upsert=False)
        if result.matched_count == 0:
            print(f'No user found with email {email}. No changes made.')
        else:
            print(f"User {email} updated to admin. Modified: {result.modified_count}")
            user = await collection.find_one({'email': email})
            print('New role:', user.get('role'))
            print('can_publish_content:', user.get('can_publish_content'))
            print('can_sell_content:', user.get('can_sell_content'))

    finally:
        client.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--email', required=True, help='Email of the existing user to promote to admin')
    p.add_argument('--publish', action='store_true', help='Grant can_publish_content')
    p.add_argument('--sell', action='store_true', help='Grant can_sell_content')
    args = p.parse_args()

    asyncio.run(make_user_admin(args.email, publish=args.publish, sell=args.sell))


if __name__ == '__main__':
    main()
