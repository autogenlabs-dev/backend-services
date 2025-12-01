from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..config import settings
# from app.auth.clerk_verifier import verify_clerk_token  # Removed - not using Clerk

router = APIRouter()


class TokenPayload(BaseModel):
    token: str


@router.post("/debug/verify-clerk")
async def debug_verify_clerk(payload: TokenPayload):
    """Dev-only endpoint to verify a Clerk token and return claims.

    Enabled only when `settings.debug` is True.
    """
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Debug endpoint disabled")

    try:
        claims = verify_clerk_token(payload.token)
        return {"claims": claims}
    except HTTPException as e:
        # Re-raise HTTPExceptions from verifier
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
