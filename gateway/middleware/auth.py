from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from jose import JWTError, jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
PUBLIC_PATHS = ["/auth/login", "/auth/register", "/health", "/docs", "/openapi.json"]

# Allow tests to inject a different session factory
_session_factory = None

def set_session_factory(factory):
    global _session_factory
    _session_factory = factory

def _get_session():
    if _session_factory:
        return _session_factory()
    from ..database import SessionLocal
    return SessionLocal()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Always pass OPTIONS through — needed for CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        if any(request.url.path.startswith(p) for p in PUBLIC_PATHS):
            return await call_next(request)

        # Try X-API-Key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            from ..models.api_key import APIKey
            db = _get_session()
            try:
                key_hash = APIKey.hash_key(api_key)
                key_obj = db.query(APIKey).filter(
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True
                ).first()
                if key_obj:
                    request.state.user_id = key_obj.owner_id
                    request.state.role = "user"
                    request.state.auth_method = "api_key"
                    return await call_next(request)
            finally:
                db.close()
            return JSONResponse({"detail": "Invalid API key"}, status_code=401)

        # Fall back to JWT
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return JSONResponse({"detail": "Missing authentication"}, status_code=401)

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload.get("sub")
            request.state.role = payload.get("role", "user")
            request.state.auth_method = "jwt"
        except JWTError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        return await call_next(request)
