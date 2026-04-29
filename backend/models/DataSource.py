from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from db.mysql import Base

class DataSource(Base):
    __tablename__ = "DataSource"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    webpage_id = Column(Integer, ForeignKey("Webpage.id", ondelete="CASCADE"), nullable=False)
    publisher = Column(String(255))
    publish_time = Column(DateTime, nullable=True)
    source_url = Column(String(2048))
