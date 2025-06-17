#!/usr/bin/env python3
"""Add password_hash column to users table."""

import sqlite3

def add_password_hash_column():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # Add the password_hash column
        cursor.execute('ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)')
        conn.commit()
        print("Successfully added password_hash column to users table")
        
        # Verify the change
        cursor.execute('PRAGMA table_info(users)')
        print("\nUpdated users table structure:")
        for row in cursor.fetchall():
            print(f"  {row}")
            
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("password_hash column already exists")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_password_hash_column()
