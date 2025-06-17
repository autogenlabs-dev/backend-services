import sqlite3
import sys

print("Starting database check...", flush=True)

try:
    conn = sqlite3.connect('test.db')
    print("Connected to database", flush=True)
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables:", flush=True)
    for table in tables:
        print(f"  - {table[0]}", flush=True)
    
    conn.close()
    print("Database check completed successfully!", flush=True)
    
except Exception as e:
    print(f"Error: {e}", flush=True)
    sys.exit(1)
