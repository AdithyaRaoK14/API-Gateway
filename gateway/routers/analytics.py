from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..database import get_db
from ..models.log import RequestLog
from ..models.api_key import APIKey

router = APIRouter()

@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    total = db.query(func.count(RequestLog.id)).scalar()
    errors = db.query(func.count(RequestLog.id)).filter(RequestLog.status_code >= 400).scalar()
    avg_latency = db.query(func.avg(RequestLog.latency_ms)).scalar()
    rate_limited = db.query(func.count(RequestLog.id)).filter(RequestLog.status_code == 429).scalar()
    return {
        "total_requests": total,
        "error_count": errors,
        "avg_latency_ms": round(avg_latency or 0, 2),
        "rate_limit_violations": rate_limited,
        "success_rate": round(((total - errors) / total * 100) if total else 0, 1)
    }

@router.get("/top-routes")
def top_routes(db: Session = Depends(get_db)):
    rows = db.query(RequestLog.path, func.count(RequestLog.id).label("count"),
                    func.avg(RequestLog.latency_ms).label("avg_latency"))\
             .group_by(RequestLog.path)\
             .order_by(func.count(RequestLog.id).desc()).limit(10).all()
    return [{"path": r.path, "count": r.count, "avg_latency_ms": round(r.avg_latency or 0, 1)} for r in rows]

@router.get("/errors")
def errors(db: Session = Depends(get_db)):
    rows = db.query(RequestLog).filter(RequestLog.status_code >= 400)\
             .order_by(RequestLog.timestamp.desc()).limit(50).all()
    return [{"path": l.path, "method": l.method, "status": l.status_code,
             "latency_ms": l.latency_ms, "user": l.user_id, "time": str(l.timestamp)} for l in rows]

@router.get("/recent")
def recent(db: Session = Depends(get_db)):
    logs = db.query(RequestLog).order_by(RequestLog.timestamp.desc()).limit(50).all()
    return [{"path": l.path, "method": l.method, "status": l.status_code,
             "latency_ms": l.latency_ms, "user": l.user_id, "time": str(l.timestamp)} for l in logs]

@router.get("/status-breakdown")
def status_breakdown(db: Session = Depends(get_db)):
    rows = db.query(RequestLog.status_code, func.count(RequestLog.id).label("count"))\
             .group_by(RequestLog.status_code).all()
    return [{"status_code": r.status_code, "count": r.count} for r in rows]

@router.get("/traffic")
def traffic(db: Session = Depends(get_db)):
    """Requests per minute for the last 60 minutes (bucketed)"""
    from datetime import datetime, timedelta
    from sqlalchemy import text
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=1)
    logs = db.query(RequestLog).filter(RequestLog.timestamp >= cutoff).all()
    buckets: dict = {}
    for log in logs:
        if log.timestamp:
            minute = log.timestamp.strftime("%H:%M")
            buckets[minute] = buckets.get(minute, 0) + 1
    return [{"time": k, "requests": v} for k, v in sorted(buckets.items())]

@router.get("/services-health")
def services_health(db: Session = Depends(get_db)):
    from ..models.service import Service
    services = db.query(Service).all()
    return [{"name": s.name, "url": s.url, "prefix": s.prefix,
             "is_healthy": s.is_healthy, "rate_limit": s.rate_limit} for s in services]
