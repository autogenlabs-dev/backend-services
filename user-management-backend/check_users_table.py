#!/usr/bin/env python3
"""Check the structure of users table."""

import sqlite3

def check_users_table():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    print("Users table structure:")
    cursor.execute('PRAGMA table_info(users)')
    for row in cursor.fetchall():
        print(f"  {row}")
    
    conn.close()

if __name__ == "__main__":
    check_users_table()
