#!/usr/bin/env python3
"""
Recreate test user with the specific ID to match JWT token.
"""

import uuid
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.services.user_service import get_password_hash

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Test user data
TEST_USER_ID = uuid.UUID("cbc70bb4-df9a-466c-8597-78b88f4287da")
TEST_USER = {
    "email": "testuser234@example.com",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User"
}

def recreate_test_user():
    """Recreate the test user with the specific ID."""
    db: Session = SessionLocal()
    try:
        # Check if user already exists with the ID
        existing_user = db.query(User).filter(User.id == str(TEST_USER_ID)).first()
        if existing_user:
            print(f"User with ID {TEST_USER_ID} already exists. Deleting...")
            db.delete(existing_user)
            db.commit()

        # Check if user with email exists
        existing_email_user = db.query(User).filter(User.email == TEST_USER["email"]).first()
        if existing_email_user:
            print(f"User with email {TEST_USER['email']} already exists with ID {existing_email_user.id}. Deleting...")
            db.delete(existing_email_user)
            db.commit()

        # Create the test user with the specific ID
        password_hash = get_password_hash(TEST_USER["password"])
        new_user = User(
            id=str(TEST_USER_ID),
            email=TEST_USER["email"],
            password_hash=password_hash,
            name=f"{TEST_USER['first_name']} {TEST_USER['last_name']}",
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Test user recreated successfully with ID {new_user.id} and email {new_user.email}")
    finally:
        db.close()

if __name__ == "__main__":
    recreate_test_user()
