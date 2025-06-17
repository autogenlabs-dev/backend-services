import sqlite3
import os

# Check if database exists and has tables
db_path = 'test.db'
if os.path.exists(db_path):
    print(f"Database file exists: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f'Database exists with tables: {[t[0] for t in tables]}')
    
    # Check users table specifically
    if ('users',) in tables:
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f'Users table has {user_count} records')
        
        if user_count > 0:
            cursor.execute('SELECT email FROM users LIMIT 5')
            users = cursor.fetchall()
            print(f'Sample users: {[u[0] for u in users]}')
    else:
        print('Users table does not exist')
    
    conn.close()
else:
    print('Database file does not exist')