from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root123@192.168.3.84:3306/crawler_db?charset=utf8mb4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
# In the routers with FastAPI, we can write `def create_task(db: Session = Depends(get_db))` so that this function will be called automatically
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
