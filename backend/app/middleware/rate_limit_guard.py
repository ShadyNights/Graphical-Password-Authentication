from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.security import check_rate_limit

class RateLimitGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        
        
        
        if not check_rate_limit(client_ip):
            return JSONResponse({"error": "Too Many Requests"}, status_code=429)
            
        return await call_next(request)
