#!/usr/bin/env python3
"""
Seed test components
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def seed_components():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.user_management_db
    
    components = [
        {
            'title': 'Button Component',
            'category': 'User Interface',
            'type': 'React',
            'language': 'TypeScript',
            'difficulty_level': 'Easy',
            'plan_type': 'Free',
            'pricing_inr': 0,
            'pricing_usd': 0,
            'rating': 4.5,
            'downloads': 500,
            'views': 1200,
            'likes': 45,
            'short_description': 'Customizable button component with multiple variants',
            'full_description': 'A comprehensive button component with primary, secondary, and outline variants.',
            'preview_images': [],
            'git_repo_url': 'https://github.com/example/button-component',
            'live_demo_url': 'https://react.dev',
            'dependencies': ['react', 'styled-components'],
            'tags': ['button', 'ui', 'form'],
            'developer_name': 'Jane Doe',
            'developer_experience': '4+ years',
            'is_available_for_dev': True,
            'featured': True,
            'popular': True,
            'user_id': None,
            'code': 'const Button = ({ children, variant = "primary" }) => <button className={variant}>{children}</button>;',
            'readme_content': '# Button Component\n\nA versatile button component.',
            'status': 'approved',
            'is_active': True,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        },
        {
            'title': 'Modal Component',
            'category': 'User Interface',
            'type': 'React',
            'language': 'JavaScript',
            'difficulty_level': 'Medium',
            'plan_type': 'Paid',
            'pricing_inr': 199,
            'pricing_usd': 3,
            'rating': 4.8,
            'downloads': 320,
            'views': 890,
            'likes': 67,
            'short_description': 'Responsive modal component with backdrop',
            'full_description': 'A fully featured modal component with backdrop, animations, and customizable content.',
            'preview_images': [],
            'git_repo_url': '',
            'live_demo_url': 'https://nextjs.org',
            'dependencies': ['react', 'framer-motion'],
            'tags': ['modal', 'overlay', 'popup'],
            'developer_name': 'Bob Smith',
            'developer_experience': '6+ years',
            'is_available_for_dev': True,
            'featured': False,
            'popular': True,
            'user_id': None,
            'code': 'const Modal = ({ isOpen, onClose, children }) => isOpen ? <div className="modal">{children}</div> : null;',
            'readme_content': '# Modal Component\n\nA feature-rich modal component.',
            'status': 'approved',
            'is_active': True,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
    ]
    
    await db.components.insert_many(components)
    print(f"Added {len(components)} components")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_components())
