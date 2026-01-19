#!/usr/bin/env python3
"""
Check Templates in Database - Detailed Report
Checks for clonable, usable, ads, and forms templates
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def check_templates():
    """Check templates in the database with detailed analysis"""
    client = AsyncIOMotorClient(settings.database_url)
    db = client.user_management_db
    templates = db.templates
    
    # Get total count
    total = await templates.count_documents({})
    print(f'\n{"="*60}')
    print(f'  TEMPLATE DATABASE REPORT')
    print(f'{"="*60}')
    print(f'\n📊 TOTAL TEMPLATES: {total}')
    
    # Get clonable templates (have git_repo_url that is not empty)
    clonable_query = {'git_repo_url': {'$exists': True, '$ne': None, '$ne': ''}}
    clonable = await templates.count_documents(clonable_query)
    print(f'\n📦 CLONABLE (with git_repo_url): {clonable}')
    
    # Get usable templates (have live_demo_url that is not empty)
    usable_query = {'live_demo_url': {'$exists': True, '$ne': None, '$ne': ''}}
    usable = await templates.count_documents(usable_query)
    print(f'🌐 USABLE (with live_demo_url): {usable}')
    
    # Get ads/advertisement/banner templates
    ads_query = {
        '$or': [
            {'category': {'$regex': 'ads|advertisement|banner', '$options': 'i'}},
            {'tags': {'$in': ['ads', 'advertisement', 'banner', 'advertising']}},
            {'title': {'$regex': 'ads|advertisement|banner', '$options': 'i'}}
        ]
    }
    ads = await templates.count_documents(ads_query)
    print(f'📢 ADS templates: {ads}')
    
    # Get forms templates
    forms_query = {
        '$or': [
            {'category': {'$regex': 'form|input', '$options': 'i'}},
            {'tags': {'$in': ['forms', 'form', 'input', 'contact', 'signup', 'login']}},
            {'title': {'$regex': 'form|contact|signup|login', '$options': 'i'}}
        ]
    }
    forms = await templates.count_documents(forms_query)
    print(f'📋 FORMS templates: {forms}')
    
    # List all unique categories
    categories = await templates.distinct('category')
    print(f'\n📂 ALL CATEGORIES ({len(categories)}):')
    for cat in sorted(categories):
        count = await templates.count_documents({'category': cat})
        print(f'   • {cat}: {count} templates')
    
    # List all unique tags
    all_tags = set()
    cursor = templates.find({}, {'tags': 1})
    async for t in cursor:
        if t.get('tags'):
            all_tags.update(t.get('tags', []))
    print(f'\n🏷️  ALL UNIQUE TAGS ({len(all_tags)}):')
    print(f'   {", ".join(sorted(all_tags)[:30])}{"..." if len(all_tags) > 30 else ""}')
    
    # List templates grouped by category
    print(f'\n{"="*60}')
    print(f'  DETAILED TEMPLATE LIST')
    print(f'{"="*60}')
    
    cursor = templates.find({}).sort('category', 1)
    current_category = None
    
    async for t in cursor:
        cat = t.get('category', 'Uncategorized')
        if cat != current_category:
            current_category = cat
            print(f'\n\n📁 {cat.upper()}')
            print('-' * 40)
        
        title = t.get('title', 'N/A')
        clonable_status = '✅' if t.get('git_repo_url') else '❌'
        usable_status = '✅' if t.get('live_demo_url') else '❌'
        
        print(f'\n  📄 {title}')
        print(f'     Type: {t.get("type", "N/A")} | Plan: {t.get("plan_type", "N/A")} | Status: {t.get("approval_status", "N/A")}')
        print(f'     Clonable: {clonable_status} | Usable: {usable_status}')
        
        git_url = t.get('git_repo_url', '')
        if git_url:
            print(f'     Git: {git_url[:60]}{"..." if len(git_url) > 60 else ""}')
        
        demo_url = t.get('live_demo_url', '')
        if demo_url:
            print(f'     Demo: {demo_url[:60]}{"..." if len(demo_url) > 60 else ""}')
        
        tags = t.get('tags', [])
        if tags:
            print(f'     Tags: {", ".join(tags[:5])}{"..." if len(tags) > 5 else ""}')
    
    # Summary of clonable and usable
    print(f'\n\n{"="*60}')
    print(f'  SUMMARY')
    print(f'{"="*60}')
    
    # Templates that are both clonable AND usable
    both_query = {
        '$and': [
            {'git_repo_url': {'$exists': True, '$ne': None, '$ne': ''}},
            {'live_demo_url': {'$exists': True, '$ne': None, '$ne': ''}}
        ]
    }
    both = await templates.count_documents(both_query)
    
    # Templates that are neither clonable nor usable
    neither_query = {
        '$and': [
            {'$or': [{'git_repo_url': {'$exists': False}}, {'git_repo_url': None}, {'git_repo_url': ''}]},
            {'$or': [{'live_demo_url': {'$exists': False}}, {'live_demo_url': None}, {'live_demo_url': ''}]}
        ]
    }
    neither = await templates.count_documents(neither_query)
    
    print(f'\n✅ Both clonable AND usable: {both}')
    print(f'📦 Only clonable (no demo): {clonable - both}')
    print(f'🌐 Only usable (no git): {usable - both}')
    print(f'❌ Neither clonable nor usable: {neither}')
    print(f'\n📢 Ads templates: {ads}')
    print(f'📋 Forms templates: {forms}')
    
    await client.close()
    print(f'\n{"="*60}\n')

if __name__ == "__main__":
    asyncio.run(check_templates())
