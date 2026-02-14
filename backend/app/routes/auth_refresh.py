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
    
    
    decoded = verify_jwt_token(payload.refresh_token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid token")

    
    repo = SessionRepository(db)
    session = await repo.get_session_by_token(payload.refresh_token)
    
    
    
    
    
    
    user_id = decoded.get("sub")
    username = decoded.get("username")
    
    new_access = create_jwt_token(username, user_id) 
    new_refresh = create_jwt_token(username, user_id, expires_delta=timedelta(days=7)) 
    
    
    if session:
        
        
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
