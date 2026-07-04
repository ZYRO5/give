"""Middleware for request/response handling."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime
import time
from app.config import get_settings
from app.utils.helpers import LoggerUtilities

settings = get_settings()
logger = LoggerUtilities.setup_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        
        # Get response
        response = await call_next(request)
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Log response
        logger.info(f"Response: {response.status_code} - {duration:.2f}ms")
        
        # Add response headers
        response.headers["X-Process-Time"] = str(duration)
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return Response(
                content={"detail": "Internal server error"},
                status_code=500,
                media_type="application/json"
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_count = {}

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Check rate limit
        current_time = datetime.utcnow().minute
        key = f"{client_ip}:{current_time}"
        
        if key not in self.request_count:
            self.request_count[key] = 0
        
        self.request_count[key] += 1
        
        if self.request_count[key] > self.requests_per_minute:
            return Response(
                content={"detail": "Rate limit exceeded"},
                status_code=429,
                media_type="application/json"
            )
        
        response = await call_next(request)
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication validation."""

    async def dispatch(self, request: Request, call_next):
        # Extract token from header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            request.state.token = token
        else:
            request.state.token = None
        
        response = await call_next(request)
        return response


class CORSMiddlewareCustom(CORSMiddleware):
    """Custom CORS middleware."""

    def __init__(self, app, **kwargs):
        super().__init__(
            app,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            **kwargs
        )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware for response compression."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add compression headers if applicable
        if "gzip" in request.headers.get("Accept-Encoding", ""):
            response.headers["Content-Encoding"] = "gzip"
        
        return response
