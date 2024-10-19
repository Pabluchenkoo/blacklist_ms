from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    app_uuid = Column(String(36), nullable=False)
    blocked_reason = Column(String(255))
    request_ip = Column(String(45))
    created_at = Column(DateTime, default=func.now())
