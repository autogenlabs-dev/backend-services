#!/usr/bin/env python3
"""Check current database structure."""

import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Current tables:")
        for table in tables:
            table_name = table[0]
            print(f"\n- {table_name}")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                null_str = "NOT NULL" if not_null else "NULL"
                pk_str = "PK" if pk else ""
                print(f"  {col_name} {col_type} {null_str} {pk_str}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()
