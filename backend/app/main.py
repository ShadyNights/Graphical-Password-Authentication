import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.session import init_db
from app.routes import api_router
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.timing_guard import TimingGuardMiddleware
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIdMiddleware

PRODUCTION = os.getenv("GPA_ENV", "dev") == "production"

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        
        pass
    yield

app = FastAPI(
    title="Graphical Password Authentication",
    description="Adversarial-grade GPA with hybrid recognition + cued recall",
    version="2.0.0",
    lifespan=lifespan,
    docs_url=None if PRODUCTION else "/docs",      
    redoc_url=None if PRODUCTION else "/redoc",     
    openapi_url=None if PRODUCTION else "/openapi.json",
)


setup_logging()




app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


app.add_middleware(RequestIdMiddleware)


app.add_middleware(SecurityHeadersMiddleware)


app.add_middleware(TimingGuardMiddleware)



app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "gpa-auth", "version": "2.0.0"}
