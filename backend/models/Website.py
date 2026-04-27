from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.mysql import Base

class Website(Base):
    __tablename__ = "Website"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    domain = Column(String(255), nullable=False, unique=True)
    organization = Column(String(255))
    contact = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
