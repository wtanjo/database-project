from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from db.mysql import Base

class CrawlTask(Base):
    __tablename__ = "CrawlTask"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    target_url = Column(String(2048), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    finished_at = Column(DateTime, nullable=True)
    page_count = Column(Integer, default=0)
    error_msg = Column(Text, nullable=True)
