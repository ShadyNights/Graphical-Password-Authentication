"""
Request Guard Middleware

Applies timing padding ONLY to auth-sensitive endpoints.
Non-auth endpoints (health, docs) return immediately.

This prevents timing oracle attacks while avoiding
the BaseHTTPMiddleware stacking issue with global padding.
"""

import time
import asyncio
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("gpa.guard")

MIN_RESPONSE_MS = 180  
AUTH_PREFIXES = ("/api/auth/login", "/api/auth/register")


class TimingGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()

        response = await call_next(request)

        
        path = request.url.path
        if any(path.startswith(p) for p in AUTH_PREFIXES):
            elapsed_ms = (time.time() - start) * 1000
            if elapsed_ms < MIN_RESPONSE_MS:
                await asyncio.sleep((MIN_RESPONSE_MS - elapsed_ms) / 1000)

            response.headers["Server-Timing"] = f"total;dur={MIN_RESPONSE_MS}"

        return response
