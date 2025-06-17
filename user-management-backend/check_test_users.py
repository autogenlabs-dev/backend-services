import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Check for test users
cursor.execute("SELECT email, subscription, tokens_remaining, monthly_limit FROM users WHERE email LIKE 'test%' OR email = 'test@example.com'")
users = cursor.fetchall()

print('Test users found:')
for user in users:
    print(f'  Email: {user[0]}, Plan: {user[1]}, Tokens: {user[2]}/{user[3]}')

# Check if we have the specific test user
cursor.execute("SELECT email, password_hash FROM users WHERE email = 'test@example.com'")
test_user = cursor.fetchone()

if test_user:
    print(f'\nTest user exists: {test_user[0]}')
    print(f'Has password: {"Yes" if test_user[1] else "No"}')
else:
    print('\ntest@example.com not found in database')

conn.close()