-- Create users table with UUID support (TEXT primary key)
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    full_name TEXT,
    subscription TEXT DEFAULT 'free',
    tokens_remaining INTEGER DEFAULT 1000,
    tokens_used INTEGER DEFAULT 0,
    monthly_limit INTEGER DEFAULT 1000,
    reset_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    last_login_at TEXT
);
