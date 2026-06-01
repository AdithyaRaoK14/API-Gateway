from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from ..database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    latency_ms = Column(Integer)
    user_id = Column(String, default="anonymous")
    service = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
