from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.mysql import Base

class Website(Base):
    __tablename__ = "websites"

    website_id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
