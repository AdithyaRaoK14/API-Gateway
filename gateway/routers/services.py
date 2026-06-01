from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models.service import Service

router = APIRouter()

class ServiceRequest(BaseModel):
    name: str
    url: str
    prefix: str
    rate_limit: str = "100/minute"

@router.get("/")
def list_services(db: Session = Depends(get_db)):
    return [{"name": s.name, "url": s.url, "prefix": s.prefix,
             "is_healthy": s.is_healthy, "rate_limit": s.rate_limit} for s in db.query(Service).all()]

@router.post("/")
def register_service(req: ServiceRequest, request: Request, db: Session = Depends(get_db)):
    if getattr(request.state, "role", "user") != "admin":
        raise HTTPException(403, "Admin only")
    if db.query(Service).filter(Service.name == req.name).first():
        raise HTTPException(400, "Service already registered")
    svc = Service(**req.model_dump())
    db.add(svc)
    db.commit()
    return {"message": "Service registered", "service": req.name}

@router.delete("/{name}")
def delete_service(name: str, request: Request, db: Session = Depends(get_db)):
    if getattr(request.state, "role", "user") != "admin":
        raise HTTPException(403, "Admin only")
    svc = db.query(Service).filter(Service.name == name).first()
    if not svc:
        raise HTTPException(404, "Not found")
    db.delete(svc)
    db.commit()
    return {"message": "Deleted"}
