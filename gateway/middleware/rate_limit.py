from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import redis.asyncio as redis
import os, time

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEFAULT_LIMIT = 100
WINDOW_SECONDS = 60
PUBLIC_PATHS = ["/auth/login", "/auth/register", "/health"]

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._redis = None

    def get_redis(self):
        if self._redis is None:
            self._redis = redis.from_url(REDIS_URL, decode_responses=True)
        return self._redis

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        if any(request.url.path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        try:
            r = self.get_redis()
            identifier = getattr(request.state, "user_id", None) or request.client.host
            key = f"rate:{identifier}"
            now = int(time.time())
            window_start = now - WINDOW_SECONDS

            pipe = r.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now) + str(id(request)): now})
            pipe.zcard(key)
            pipe.expire(key, WINDOW_SECONDS)
            results = await pipe.execute()

            count = results[2]
            remaining = max(0, DEFAULT_LIMIT - count)

            if count > DEFAULT_LIMIT:
                return JSONResponse(
                    {"detail": "Rate limit exceeded", "retry_after": WINDOW_SECONDS},
                    status_code=429,
                    headers={"Retry-After": str(WINDOW_SECONDS)}
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(DEFAULT_LIMIT)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response

        except Exception:
            # Redis unavailable - allow request through (fail open)
            return await call_next(request)
