"""Password utility functions for user authentication."""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Previously hashed password
        
    Returns:
        True if password matches hash, False otherwise
    """
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False
