from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ..config import settings
# from app.auth.clerk_verifier import verify_clerk_token  # Removed - not using Clerk
from ..database import get_database
from ..models.user import User
from typing import Any
from beanie import PydanticObjectId

router = APIRouter()


class TokenPayload(BaseModel):
    token: str


@router.post("/verify-user")
async def verify_user(payload: TokenPayload, db: Any = Depends(get_database)):
    """Verify a Clerk JWT token and return the authenticated user data.

    Accepts a Clerk session JWT and returns user profile if valid.
    Creates user if they don't exist.
    """
    print(f"DEBUG: Received verify-user request with token: {payload.token[:50]}...")  # Log first 50 chars
    
    try:
        # Verify the token using Clerk verifier
        claims = verify_clerk_token(payload.token)
        print(f"DEBUG: Token verified successfully, claims: {claims}")
        
        email = claims.get("email") or claims.get("email_address")
        sub = claims.get("sub")
        first_name = claims.get("given_name") or claims.get("name", "").split(" ")[0]
        last_name = claims.get("family_name") or " ".join(claims.get("name", "").split(" ")[1:]) if claims.get("name") else ""
        
        if not email:
            # If no email in token, create a placeholder email using sub
            email = f"{sub}@clerk.user"
            print(f"DEBUG: No email in token, using placeholder: {email}")
        
        if not sub:
            print("DEBUG: Token missing sub claim")
            raise HTTPException(status_code=400, detail="Token missing sub claim")
        
        # Find existing user by email
        user = await User.find_one(User.email == email)
        print(f"DEBUG: User lookup result: {user}")
        
        if not user:
            # Create new user
            user = User(
                email=email,
                name=f"{first_name} {last_name}".strip(),
                full_name=f"{first_name} {last_name}".strip(),
                is_active=True,
                role="user"  # Use valid enum value
            )
            await user.insert()
            print(f"DEBUG: Created new user: {user.id}")
        
        return {
            "verified": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active
            },
            "claims": claims
        }
    except HTTPException as e:
        print(f"DEBUG: HTTPException during verification: {e.detail}")
        # Re-raise HTTPExceptions from verifier
        raise e
    except Exception as e:
        print(f"DEBUG: Unexpected error during verification: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")