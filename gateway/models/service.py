from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Service(Base):
    __tablename__ = "services"
    name = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    prefix = Column(String, nullable=False, unique=True)
    is_healthy = Column(Boolean, default=True)
    rate_limit = Column(String, default="100/minute")
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
