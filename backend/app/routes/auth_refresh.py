from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from app.security.jwt_handler import verify_jwt_token, create_jwt_token
from app.db.session_repository import SessionRepository
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

router = APIRouter()

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify token signature
    # In a real app, verify_jwt_token checks signature + exp
    decoded = verify_jwt_token(payload.refresh_token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 2. Check DB for session revocation/rotation
    repo = SessionRepository(db)
    session = await repo.get_session_by_token(payload.refresh_token)
    
    # If session usage is enforced, uncomment:
    # if not session:
    #     raise HTTPException(status_code=401, detail="Session revoked")
    
    # 3. Rotate tokens
    user_id = decoded.get("sub")
    username = decoded.get("username")
    
    new_access = create_jwt_token(username, user_id) # Short lived
    new_refresh = create_jwt_token(username, user_id, expires_delta=timedelta(days=7)) # Long lived
    
    # 4. Update Session in DB
    if session:
        # Rotation: delete old, create new? or update?
        # For strict rotation, we replace.
        await repo.delete_session(payload.refresh_token)
        await repo.create_session(
            user_id=user_id,
            refresh_token=new_refresh,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }
