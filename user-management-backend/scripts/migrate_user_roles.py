#!/usr/bin/env python3
"""
Safe MongoDB migration for user role -> role + capability flags.

Usage:
  MONGO_URI="mongodb://localhost:27017" DB_NAME=mydb python3 scripts/migrate_user_roles.py --dry-run
  MONGO_URI="mongodb://localhost:27017" DB_NAME=mydb python3 scripts/migrate_user_roles.py --apply

This script will:
- For each document in the `users` collection, examine existing role fields
  (e.g. `role`, `roles`, `is_developer`, `developer`) and determine the new
  canonical `role` ('ADMIN' or 'USER').
- Set capability booleans `can_publish_content` and `can_sell_content` when
  the user previously had developer privileges. It will preserve existing
  capability flags if they already exist.
- By default runs in `--dry-run` mode and prints a summary. Use `--apply` to
  perform updates. Always backup your DB first.
"""

import os
import argparse
from pymongo import MongoClient
from pprint import pformat


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true', default=False, help='Show changes but do not apply')
    p.add_argument('--apply', action='store_true', default=False, help='Apply changes to DB')
    p.add_argument('--batch', type=int, default=500, help='Documents per batch')
    return p.parse_args()


def detect_developer(user):
    # Heuristics for detecting prior 'developer' role
    roles = user.get('roles') or []
    if isinstance(roles, str):
        roles = [roles]
    old_role = user.get('role') or user.get('roles') or user.get('user_type')
    if isinstance(old_role, list):
        old_role = old_role[0] if old_role else None
    # booleans that might have been used
    if user.get('is_developer') or user.get('developer'):
        return True
    if old_role and str(old_role).lower() in ('developer', 'dev'):
        return True
    if roles and any(str(r).lower() == 'developer' for r in roles):
        return True
    return False


def map_role(old_role):
    if not old_role:
        return 'USER'
    s = str(old_role).lower()
    if s in ('superadmin', 'super-admin', 'super_admin', 'admin', 'administrator'):
        return 'ADMIN'
    return 'USER'


def main():
    args = parse_args()
    if not args.dry_run and not args.apply:
        print('Specify --dry-run or --apply')
        return

    mongo_uri = os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017')
    db_name = os.getenv('DB_NAME', os.getenv('MONGO_DB', 'userdb'))

    print(f'Connecting to {mongo_uri} db={db_name} (dry_run={args.dry_run})')
    client = MongoClient(mongo_uri)
    db = client[db_name]
    users = db.users

    total = users.count_documents({})
    print(f'Found {total} users')

    cursor = users.find({}, batch_size=args.batch)
    changes = []
    i = 0
    for u in cursor:
        i += 1
        uid = u.get('_id')
        old_role = u.get('role') or (u.get('roles')[0] if isinstance(u.get('roles'), list) and u.get('roles') else None)
        new_role = map_role(old_role)
        is_dev = detect_developer(u)

        # preserve existing capability flags if present, else set based on detected developer
        can_publish = u.get('can_publish_content', True if is_dev else False)
        can_sell = u.get('can_sell_content', True if is_dev else False)

        update = {}
        # Only update if anything would change
        if u.get('role') != new_role:
            update['role'] = new_role
        # ensure boolean fields exist
        if 'can_publish_content' not in u or u.get('can_publish_content') != can_publish:
            update['can_publish_content'] = can_publish
        if 'can_sell_content' not in u or u.get('can_sell_content') != can_sell:
            update['can_sell_content'] = can_sell

        if update:
            changes.append({'_id': uid, 'update': update})

        if i % 500 == 0:
            print(f'Processed {i}/{total} users...')

    print(f'Planned changes for {len(changes)} users')
    if args.dry_run:
        # show sample of changes
        sample = changes[:20]
        print('Sample planned updates:')
        for c in sample:
            print(pformat(c))
        print('Dry-run complete. Run with --apply to persist changes. BACKUP your DB first.')
        return

    # apply mode
    for c in changes:
        uid = c['_id']
        update = c['update']
        users.update_one({'_id': uid}, {'$set': update})

    print(f'Applied updates to {len(changes)} users')


if __name__ == '__main__':
    main()
