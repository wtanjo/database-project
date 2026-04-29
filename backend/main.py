from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tasks, contents, images, websites, webpages, stats
from db.mysql import Base, engine
import models.CrawlTask
import models.Website
import models.Webpage
import models.DataSource

Base.metadata.create_all(bind=engine)

app = FastAPI(title="网络数据爬取管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(contents.router)
app.include_router(images.router)
app.include_router(websites.router)
app.include_router(webpages.router)
app.include_router(stats.router)


@app.get("/")
def welcome():
    return {"message": "Crawler System API Running", "docs": "/docs"}
