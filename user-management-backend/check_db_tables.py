#!/usr/bin/env python3
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result]
    print(f"Tables in database: {tables}")
    
    # Check if users table has stripe_customer_id column
    if 'users' in tables:
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        print(f"Users table columns: {columns}")
        print(f"Has stripe_customer_id: {'stripe_customer_id' in columns}")
