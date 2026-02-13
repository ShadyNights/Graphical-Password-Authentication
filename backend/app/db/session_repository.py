from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.models import Session
from datetime import datetime

class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: str, refresh_token: str, expires_at: datetime, device_hash: str = None):
        session = Session(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            device_hash=device_hash
        )
        self.db.add(session)
        await self.db.commit()
        return session

    async def get_session_by_token(self, refresh_token: str):
        result = await self.db.execute(select(Session).where(Session.refresh_token == refresh_token))
        return result.scalar_one_or_none()

    async def delete_session(self, refresh_token: str):
        await self.db.execute(delete(Session).where(Session.refresh_token == refresh_token))
        await self.db.commit()

    async def cleanup_expired_sessions(self):
        # Implementation depends on DB dialect, simple delete for now
        await self.db.execute(delete(Session).where(Session.expires_at < datetime.utcnow()))
        await self.db.commit()
