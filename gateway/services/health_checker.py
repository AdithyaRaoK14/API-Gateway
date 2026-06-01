import httpx
import asyncio
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.service import Service

class HealthChecker:
    async def start(self):
        while True:
            await self.check_all()
            await asyncio.sleep(30)

    async def check_all(self):
        db: Session = SessionLocal()
        try:
            services = db.query(Service).all()
            for svc in services:
                try:
                    async with httpx.AsyncClient(timeout=3.0) as client:
                        resp = await client.get(f"{svc.url}/health")
                    svc.is_healthy = resp.status_code == 200
                except Exception:
                    svc.is_healthy = False
            db.commit()
        finally:
            db.close()
