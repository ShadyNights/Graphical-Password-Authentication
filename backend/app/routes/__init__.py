from fastapi import APIRouter
from .auth_init import router as init_router
from .auth_register import router as register_router
from .auth_login import router as login_router
from .totp import router as totp_router
from .auth_refresh import router as refresh_router

api_router = APIRouter(prefix="/api/auth")


api_router.include_router(init_router, tags=["auth"])


api_router.include_router(register_router, tags=["auth"])


api_router.include_router(login_router, tags=["auth"])


api_router.include_router(totp_router, tags=["totp"])


api_router.include_router(refresh_router, tags=["auth"])
