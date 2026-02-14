from typing import Generator
from app.db.session import SessionLocal


async def get_db() -> Generator:
    async with SessionLocal() as session:
        yield session


def get_hsm_client():
    from app.security.hsm_client import keys
    return keys


async def get_redis():
    
    return None
