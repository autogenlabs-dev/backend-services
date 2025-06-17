#!/usr/bin/env python3
"""Add organization tables to database."""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def migrate_database():
    """Create organization tables."""
    print("Creating organization tables...")
    
    try:
        # Import the database setup
        from app.database import engine, Base
        
        # Import all models to ensure they're registered with Base
        from app.models.user import (
            User, OAuthProvider, UserOAuthAccount, SubscriptionPlan, 
            UserSubscription, TokenUsageLog, ApiKey,
            Organization, OrganizationMember, OrganizationInvitation,
            OrganizationKey, KeyUsageLog
        )
          print("Models imported successfully")
        
        # Create only the organization tables
        print("Creating tables...")
        
        # We need to use create_all for proper foreign key detection,
        # but we'll check first if tables already exist to avoid conflicts
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Check which tables need to be created
        tables_to_create = []
        org_tables = {
            "organizations": Organization.__table__,
            "organization_keys": OrganizationKey.__table__,
            "organization_members": OrganizationMember.__table__, 
            "organization_invitations": OrganizationInvitation.__table__,
            "key_usage_logs": KeyUsageLog.__table__
        }
        
        for name, table in org_tables.items():
            if name not in tables:
                print(f"Creating {name} table...")
                tables_to_create.append(table)
            else:
                print(f"Table {name} already exists, skipping...")
        
        # Create the tables that don't exist yet
        if tables_to_create:
            # Use MetaData to create all tables at once with proper dependency order
            from sqlalchemy import MetaData
            metadata = MetaData()
            for table in tables_to_create:
                table.tometadata(metadata)
            metadata.create_all(engine)
          print("Organization tables created successfully!")
        
        # Verify all tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        org_tables = ['organizations', 'organization_keys', 'organization_members', 'organization_invitations', 'key_usage_logs']
        for table in org_tables:
            if table in tables:
                print(f"✅ {table} table created")
            else:
                print(f"❌ {table} table NOT created")
                
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_database()
