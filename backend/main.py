from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tasks, contents# , images
from db.mysql import Base, engine
import models.CrawlTask  # ensure model is registered before create_all

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crawler System MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(contents.router)
# app.include_router(images.router)

@app.get("/")
def welcome():
    return {"message": "API Running"}
