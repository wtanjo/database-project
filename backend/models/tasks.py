from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.mysql import Base

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    task_url = Column(String(255), nullable=False)
    task_status = Column(String(50), default="pending") # pending, running, completed, error
    created_at = Column(DateTime, default=datetime.now)
