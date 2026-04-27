from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tasks, contents# , images

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
