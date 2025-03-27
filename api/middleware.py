"""
Middleware for the FastAPI application.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from config.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and log details."""
        start_time = time.time()
        
        # Get client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Log the request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip}"
        )
        
        try:
            response = await call_next(request)
            
            # Log the response
            process_time = time.time() - start_time
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"status_code={response.status_code} "
                f"completed_in={process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error processing request: {request.method} "
                f"{request.url.path} - {str(e)}"
            )
            
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Basic rate limiting middleware.
    
    In a production application, use a more robust solution like Redis-based
    rate limiting or a service like CloudFlare.
    """
    
    def __init__(self, app, requests_per_minute=60):
        """Initialize with configurable rate limit."""
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
    
    async def dispatch(self, request: Request, call_next):
        """Process the request with rate limiting."""
        # Get client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        current_time = int(time.time() / 60)  # Current minute
        
        # Clean up old entries
        self.request_counts = {
            ip_time: count 
            for ip_time, count in self.request_counts.items() 
            if ip_time[1] == current_time
        }
        
        # Check and update request count
        key = (client_ip, current_time)
        current_count = self.request_counts.get(key, 0)
        
        if current_count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later."
                },
            )
        
        self.request_counts[key] = current_count + 1
        
        return await call_next(request) 