#!/usr/bin/env python3
"""Add expires_at column to api_keys table."""

import sqlite3

def add_expires_at_column():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # Add the expires_at column
        cursor.execute('ALTER TABLE api_keys ADD COLUMN expires_at DATETIME')
        conn.commit()
        print("Successfully added expires_at column to api_keys table")
        
        # Verify the change
        cursor.execute('PRAGMA table_info(api_keys)')
        print("\nUpdated api_keys table structure:")
        for row in cursor.fetchall():
            print(f"  {row}")
            
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("expires_at column already exists")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_expires_at_column()
