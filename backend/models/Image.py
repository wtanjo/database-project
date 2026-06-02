from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from db.mysql import Base


class Image(Base):
    __tablename__ = "Image"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    webpage_id = Column(
        Integer, ForeignKey("Webpage.id", ondelete="CASCADE"), nullable=False
    )
    image_url = Column(String(2048), nullable=False)
    description = Column(String(1024))
    crawl_time = Column(DateTime, default=datetime.now)
