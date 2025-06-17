import sqlite3

# Direct SQLite connection test
conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", [table[0] for table in tables])

# Get count of records in each table
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Records in {table_name}: {count}")

conn.close()
