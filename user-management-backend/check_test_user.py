import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Check for test users
cursor.execute('''
    SELECT email, subscription, tokens_remaining, monthly_limit, password_hash, is_active 
    FROM users 
    WHERE email LIKE "test%" 
    ORDER BY email
''')
users = cursor.fetchall()

print('Test users found:')
if users:
    for user in users:
        email, subscription, tokens_remaining, monthly_limit, password_hash, is_active = user
        has_password = "Yes" if password_hash else "No"
        print(f'  Email: {email}')
        print(f'    Plan: {subscription}')
        print(f'    Tokens: {tokens_remaining}/{monthly_limit}')
        print(f'    Password: {has_password}')
        print(f'    Active: {is_active}')
        print()
else:
    print('  No test users found')

# Check specifically for test@example.com
cursor.execute('SELECT * FROM users WHERE email = "test@example.com"')
specific_user = cursor.fetchone()

if specific_user:
    print('test@example.com user details:')
    print(f'  Found user with password: {"Yes" if specific_user[2] else "No"}')
else:
    print('test@example.com user not found')

conn.close()