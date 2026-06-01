from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
import asyncio

from .routers import auth, services, analytics, api_keys
from .middleware.auth import AuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .database import engine, Base, get_db
from .services.health_checker import HealthChecker
from .services.router_service import RouteResolver
from .models.log import RequestLog

health_checker = HealthChecker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    task = asyncio.create_task(health_checker.start())
    yield
    task.cancel()

app = FastAPI(title="API Gateway", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(services.router, prefix="/services", tags=["services"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(path: str, request: Request):
    import time
    from sqlalchemy.orm import Session

    db: Session = next(get_db())
    start = time.time()

    resolver = RouteResolver(db)
    target = resolver.resolve(path)

    if not target:
        db.close()
        return Response(content='{"detail":"No route matched"}', status_code=404, media_type="application/json")

    url = f"{target}/{path}"
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request(request.method, url, headers=headers,
                                        content=body, params=dict(request.query_params))
        status = resp.status_code
        response_body = resp.content
    except Exception as e:
        status = 502
        response_body = f'{{"detail":"Upstream error: {str(e)}"}}'.encode()

    latency = int((time.time() - start) * 1000)
    user = getattr(request.state, "user_id", "anonymous")

    log = RequestLog(path=f"/{path}", method=request.method, status_code=status,
                     latency_ms=latency, user_id=user, service=target)
    db.add(log)
    db.commit()
    db.close()

    return Response(content=response_body, status_code=status, media_type="application/json")

@app.get("/health")
def health():
    return {"status": "ok"}
