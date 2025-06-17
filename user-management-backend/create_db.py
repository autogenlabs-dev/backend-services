#!/usr/bin/env python3
"""
Create a simple SQLite database for the backend authentication tests
"""

import sqlite3
import os
from datetime import datetime

def create_database():
    db_path = r"C:\Users\Asus\Music\autogen-backend\user-management-backend\test.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        except PermissionError:
            print(f"Cannot remove database - file may be in use by the server")
            print("Please stop the server first, then run this script again")
            return False
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                full_name TEXT,
                subscription TEXT DEFAULT 'free',
                tokens_remaining INTEGER DEFAULT 1000,
                tokens_used INTEGER DEFAULT 0,
                monthly_limit INTEGER DEFAULT 1000,
                reset_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                last_login_at TEXT
            )
        ''')
        
        # Create oauth_providers table
        cursor.execute('''
            CREATE TABLE oauth_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Insert default OAuth providers
        cursor.execute('''
            INSERT INTO oauth_providers (name, display_name, is_active)
            VALUES ('openrouter', 'OpenRouter', 1)
        ''')
        
        cursor.execute('''
            INSERT INTO oauth_providers (name, display_name, is_active)
            VALUES ('requesty', 'Requesty', 1)
        ''')
        
        conn.commit()
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ Database created successfully!")
        print(f"📋 Tables created: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    create_database()
