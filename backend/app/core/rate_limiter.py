"""
Rate Limiting Middleware for FastAPI
Uses Redis for distributed rate limiting across multiple instances
"""
import time
import logging
from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
import hashlib

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration for different endpoints"""
    
    # Default: 100 requests per minute
    DEFAULT = {"requests": 100, "window": 60}
    
    # Auth endpoints: 5 requests per minute (prevent brute force)
    AUTH = {"requests": 5, "window": 60}
    
    # Login specifically: 5 attempts per 5 minutes
    LOGIN = {"requests": 5, "window": 300}
    
    # File upload: 10 per minute
    UPLOAD = {"requests": 10, "window": 60}
    
    # Analysis: 20 per minute (CPU intensive)
    ANALYSIS = {"requests": 20, "window": 60}
    
    # History/Dashboard: 60 per minute
    READ = {"requests": 60, "window": 60}


class RateLimiter:
    """Redis-based rate limiter with sliding window"""
    
    def __init__(self):
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=1,  # Use different DB for rate limiting
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            self.redis.ping()
            self.enabled = True
            logger.info("Rate limiter connected to Redis")
        except redis.ConnectionError:
            self.redis = None
            self.enabled = False
            logger.warning("Rate limiter Redis connection failed - rate limiting disabled")
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit key"""
        endpoint_hash = hashlib.md5(endpoint.encode()).hexdigest()[:8]
        return f"ratelimit:{identifier}:{endpoint_hash}"
    
    def is_rate_limited(
        self, 
        identifier: str, 
        endpoint: str, 
        max_requests: int, 
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request should be rate limited using sliding window
        Returns: (is_limited, info_dict)
        """
        if not self.enabled or not self.redis:
            return False, {"remaining": max_requests, "reset": 0}
        
        try:
            key = self._get_key(identifier, endpoint)
            now = time.time()
            window_start = now - window_seconds
            
            pipe = self.redis.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiry on the key
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            request_count = results[1]
            
            remaining = max(0, max_requests - request_count - 1)
            reset_time = int(window_start + window_seconds)
            
            info = {
                "remaining": remaining,
                "limit": max_requests,
                "reset": reset_time,
                "window": window_seconds
            }
            
            if request_count >= max_requests:
                # Remove the request we just added since it's over limit
                self.redis.zrem(key, str(now))
                return True, info
            
            return False, info
            
        except redis.RedisError as e:
            logger.error(f"Rate limiter Redis error: {e}")
            return False, {"remaining": max_requests, "reset": 0}
    
    def get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier from request"""
        # Try to get real IP behind proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        # For authenticated requests, also consider user
        # This allows per-user rate limiting
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_hash = hashlib.md5(auth_header.encode()).hexdigest()[:8]
            return f"{ip}:{token_hash}"
        
        return ip


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app):
        super().__init__(app)
        self.limiter = RateLimiter()
        
        # Endpoint patterns and their rate limit configs
        self.endpoint_configs = [
            (r"/api/v1/auth/login", RateLimitConfig.LOGIN),
            (r"/api/v1/auth/register", RateLimitConfig.AUTH),
            (r"/api/v1/auth/", RateLimitConfig.AUTH),
            (r"/api/v1/resume/upload", RateLimitConfig.UPLOAD),
            (r"/api/v1/resume/analyze", RateLimitConfig.ANALYSIS),
            (r"/api/v1/resume/history", RateLimitConfig.READ),
            (r"/api/v1/resume/dashboard", RateLimitConfig.READ),
            (r"/api/v1/score/", RateLimitConfig.ANALYSIS),
        ]
    
    def _get_config_for_endpoint(self, path: str) -> dict:
        """Get rate limit config for endpoint"""
        for pattern, config in self.endpoint_configs:
            if path.startswith(pattern.replace(r"/", "/")):
                return config
        return RateLimitConfig.DEFAULT
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks and docs
        path = request.url.path
        if path in ["/health", "/docs", "/redoc", "/openapi.json", "/"]:
            return await call_next(request)
        
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Get rate limit config for this endpoint
        config = self._get_config_for_endpoint(path)
        
        # Check rate limit
        identifier = self.limiter.get_client_identifier(request)
        is_limited, info = self.limiter.is_rate_limited(
            identifier=identifier,
            endpoint=path,
            max_requests=config["requests"],
            window_seconds=config["window"]
        )
        
        if is_limited:
            logger.warning(f"Rate limit exceeded for {identifier} on {path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please slow down.",
                    "retry_after": info.get("reset", 60) - int(time.time())
                },
                headers={
                    "X-RateLimit-Limit": str(info.get("limit", 0)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info.get("reset", 0)),
                    "Retry-After": str(info.get("reset", 60) - int(time.time()))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", 0))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(info.get("reset", 0))
        
        return response


# Decorator for function-level rate limiting
def rate_limit(requests: int = 10, window: int = 60):
    """Decorator for rate limiting specific endpoints"""
    def decorator(func: Callable):
        limiter = RateLimiter()
        
        async def wrapper(request: Request, *args, **kwargs):
            identifier = limiter.get_client_identifier(request)
            endpoint = f"{func.__module__}.{func.__name__}"
            
            is_limited, info = limiter.is_rate_limited(
                identifier=identifier,
                endpoint=endpoint,
                max_requests=requests,
                window_seconds=window
            )
            
            if is_limited:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                    headers={"Retry-After": str(info.get("reset", 60) - int(time.time()))}
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator
