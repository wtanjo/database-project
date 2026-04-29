import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Index
from db.mysql import Base


class Status(str, enum.Enum):
    PENDING = 'pending'
    FETCHING = 'fetching'
    SUCCESS = 'success'
    FAILED = 'failed'
    INVALID = 'invalid'


class Webpage(Base):
    __tablename__ = "Webpage"
    # url 最长 2048 字符，utf8mb4 下全列索引超过 3072 字节限制
    # 用前缀索引（768 字符 × 4 字节 = 3072 字节）保证唯一性
    __table_args__ = (
        Index('uq_webpage_url', 'url', unique=True, mysql_length=768),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(2048), nullable=False)          # unique 由 __table_args__ 的前缀索引保证
    website_id = Column(Integer, ForeignKey("Website.id", ondelete="CASCADE"))
    crawl_time = Column(DateTime, nullable=False)
    status = Column(
        Enum(Status, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=Status.PENDING,
    )
    title = Column(String(512))
