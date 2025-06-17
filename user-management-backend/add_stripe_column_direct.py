#!/usr/bin/env python3
import sqlite3

try:
    # Connect directly to SQLite database
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    if 'stripe_customer_id' not in columns:
        # Add the column
        cursor.execute("ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255)")
        conn.commit()
        print("Added stripe_customer_id column successfully")
        
        # Verify it was added
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Updated columns: {columns}")
    else:
        print("stripe_customer_id column already exists")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
