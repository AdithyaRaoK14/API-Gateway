from sqlalchemy.orm import Session
from ..models.service import Service

class RouteResolver:
    def __init__(self, db: Session):
        self.db = db

    def resolve(self, path: str):
        services = self.db.query(Service).filter(Service.is_healthy == True).all()
        for svc in services:
            prefix = svc.prefix.strip("/")
            if path.startswith(prefix):
                return svc.url.rstrip("/")
        return None
