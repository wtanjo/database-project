import enum
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.mysql import Base

class Status(enum.Enum):
    PENDING = 'pending'
    FETCHING = 'fetching'
    SUCCESS = 'success'
    FAILED = 'failed'
    INVALID = 'invalid'

class Webpage(Base):
    __tablename__ = "Webpage"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(2048), nullable=False, unique=True)
    website_id = Column(Integer, ForeignKey("Website.id", ondelete="CASCADE"))
    crawl_time = Column(DateTime, nullable=False)
    status = Column(sqlalchemy.Enum(Status), nullable=False, default=Status.PENDING)
    title = Column(String(512))
