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
        
        # Check if Organization class is properly defined
        print(f"Organization table name: {Organization.__tablename__}")
        print(f"Organization columns: {[c.name for c in Organization.__table__.columns]}")
        print(f"OrganizationKey table name: {OrganizationKey.__tablename__}")
        
        # Direct approach: create all tables at once
        print("Creating all organization tables...")
        
        try:
            # Create tables explicitly with bind parameter
            Organization.__table__.create(bind=engine, checkfirst=True)
            print("Organization table created")
            
            OrganizationKey.__table__.create(bind=engine, checkfirst=True)
            print("OrganizationKey table created")
            
            OrganizationMember.__table__.create(bind=engine, checkfirst=True)
            print("OrganizationMember table created")
            
            OrganizationInvitation.__table__.create(bind=engine, checkfirst=True)
            print("OrganizationInvitation table created")
            
            KeyUsageLog.__table__.create(bind=engine, checkfirst=True)
            print("KeyUsageLog table created")
        except Exception as e:
            print(f"Error during table creation: {e}")
            import traceback
            traceback.print_exc()
        
        print("Organization tables created successfully!")
          # Verify all tables were created
        from sqlalchemy import inspect
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
