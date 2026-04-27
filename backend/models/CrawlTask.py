import enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from datetime import datetime
from db.mysql import Base

class Status(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class CrawlTask(Base):
    __tablename__ = "CrawlTask"

    id = Column(Integer, primary_key=True, autoincrement=True, index=Trueb)
    target_url = Column(String(2048), nullable=False)
    status = Column(sqlalchemy.Enum(Status), default=Status.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    finished_at = Column(DateTime, nullable=True)
    page_count = Column(Integer, default=0)
    error_msg = Column(Text, nullable=True)
