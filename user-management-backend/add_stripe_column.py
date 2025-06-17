#!/usr/bin/env python3
from app.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result]
        
        if 'stripe_customer_id' not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255)"))
            conn.commit()
            print("Added stripe_customer_id column successfully")
        else:
            print("stripe_customer_id column already exists")
            
except Exception as e:
    print(f"Error: {e}")
