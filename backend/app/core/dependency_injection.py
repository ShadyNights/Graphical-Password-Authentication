from typing import Generator
from app.db.session import SessionLocal

# Dependency for DB Session
async def get_db() -> Generator:
    async with SessionLocal() as session:
        yield session

# Dependency for HSM (Singleton verification)
def get_hsm_client():
    from app.security.hsm_client import keys
    return keys

# Dependency for Redis (Stub)
async def get_redis():
    # In production: return aioredis pool
    return None
