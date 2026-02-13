import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./gpa.db"
    REDIS_URL: str = "redis://localhost:6379"
    GPA_SECRET_KEY: str = os.getenv("GPA_SECRET_KEY", "dev-secret-key-change-in-production-immediately")
    GPA_PEPPER: str = os.getenv("GPA_PEPPER", "dev-pepper-value-store-in-hsm")
    GPA_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 15
    MAX_FAILED_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 600
    RATE_LIMIT_MAX_REQUESTS: int = 20
    ARGON2_MEMORY_COST: int = 65536  # 64MB
    ARGON2_TIME_COST: int = 2
    ARGON2_PARALLELISM: int = 2
    CLICK_TOLERANCE: float = 0.05  # 5% normalized radius
    REQUIRED_IMAGE_SELECTIONS: int = 3
    REQUIRED_CLICK_POINTS: int = 6
    TOTAL_IMAGES_SHOWN: int = 12
    CONSTANT_RESPONSE_MS: int = 160  # Target constant response time

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
