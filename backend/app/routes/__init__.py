from fastapi import APIRouter
from .auth_init import router as init_router
from .auth_register import router as register_router
from .auth_login import router as login_router
from .totp import router as totp_router
from .auth_refresh import router as refresh_router

api_router = APIRouter(prefix="/api/auth")

# Init router handles /challenge, /images
api_router.include_router(init_router, tags=["auth"])

# Register router handles /register
api_router.include_router(register_router, tags=["auth"])

# Login router handles /login
api_router.include_router(login_router, tags=["auth"])

# TOTP router handles /totp/*
api_router.include_router(totp_router, tags=["totp"])

# Refresh router handles /refresh
api_router.include_router(refresh_router, tags=["auth"])
