#!/usr/bin/env python3
"""
Create a local JWT signed with app's secret for testing endpoints without Clerk.

Usage:
  export MONGO_URI='mongodb://localhost:27017'
  export DB_NAME='user_management_db'
  python3 scripts/create_local_jwt.py --email test@example.com --name test_user

Options:
  --admin         Create an ADMIN role user
  --publish       Grant `can_publish_content` capability
"""
import os
import asyncio
import argparse
from datetime import timedelta

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.user import User, UserRole
from app.config import settings
from app.auth.jwt import create_access_token
from app.models.template import Template, TemplateCategory, TemplateLike
from app.models.component import Component


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', required=True)
    parser.add_argument('--name', required=False, default='testuser')
    parser.add_argument('--admin', action='store_true')
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()

    mongo_uri = os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017')
    db_name = os.getenv('DB_NAME', 'user_management_db')

    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]

    # Initialize beanie models
    await init_beanie(database=db, document_models=[User, Template, TemplateCategory, TemplateLike, Component])

    # Find or create user
    user = await User.find_one(User.email == args.email)
    if not user:
        role = UserRole.ADMIN if args.admin else UserRole.USER
        user = User(email=args.email, name=args.name, role=role, is_active=True)
        if args.publish:
            user.can_publish_content = True
        await user.insert()
        print(f"Created user {user.email} with id {user.id} and role {user.role}")
    else:
        print(f"Found existing user {user.email} id={user.id} role={user.role}")

    token_data = {"sub": str(user.id), "email": user.email}
    token = create_access_token(token_data, expires_delta=timedelta(days=1))
    print("\nLocal access token (paste into USER_TOKEN):\n")
    print(token)

if __name__ == '__main__':
    asyncio.run(main())
