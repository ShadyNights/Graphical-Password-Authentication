from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import logging

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # Add to context if using context vars
        # context.set("request_id", request_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
