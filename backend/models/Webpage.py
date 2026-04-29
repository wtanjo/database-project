import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from db.mysql import Base


class Status(str, enum.Enum):
    PENDING = 'pending'
    FETCHING = 'fetching'
    SUCCESS = 'success'
    FAILED = 'failed'
    INVALID = 'invalid'


class Webpage(Base):
    __tablename__ = "Webpage"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(768), nullable=False, unique=True)
    website_id = Column(Integer, ForeignKey("Website.id", ondelete="CASCADE"))
    crawl_time = Column(DateTime, nullable=False)
    status = Column(Enum(Status, values_callable=lambda x: [e.value for e in x]), nullable=False, default=Status.PENDING)
    title = Column(String(512))
