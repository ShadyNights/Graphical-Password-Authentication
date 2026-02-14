"""
Security Headers Middleware

Injects hardened HTTP response headers on every response:
- X-Content-Type-Options: nosniff (prevents MIME sniffing)
- X-Frame-Options: DENY (prevents clickjacking)
- Strict-Transport-Security: HSTS 2-year max-age
- Content-Security-Policy: strict default-src
- Referrer-Policy: no-referrer (prevents referer leaks)
- X-XSS-Protection: block mode
- Permissions-Policy: restrict dangerous APIs
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        
        response.headers["X-Content-Type-Options"] = "nosniff"

        
        response.headers["X-Frame-Options"] = "DENY"

        
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )

        
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "frame-ancestors 'none'"
        )

        
        response.headers["Referrer-Policy"] = "no-referrer"

        
        response.headers["X-XSS-Protection"] = "1; mode=block"

        
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        return response
