from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from db.mysql import get_db
from db.mongo import contents_collection, images_collection
from models.CrawlTask import CrawlTask
from models.Website import Website
from models.Webpage import Webpage
from utils import success

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
def get_stats(db: Session = Depends(get_db)):
    """返回系统整体统计数据（任务数、网站数、内容数、图片数）。"""
    task_total = db.query(func.count(CrawlTask.id)).scalar()
    task_running = db.query(func.count(CrawlTask.id)).filter(CrawlTask.status == "running").scalar()
    task_completed = db.query(func.count(CrawlTask.id)).filter(CrawlTask.status == "completed").scalar()
    task_failed = db.query(func.count(CrawlTask.id)).filter(CrawlTask.status == "failed").scalar()

    website_total = db.query(func.count(Website.id)).scalar()
    webpage_total = db.query(func.count(Webpage.id)).scalar()

    content_total = contents_collection.count_documents({})
    image_total = images_collection.count_documents({})

    # 按网站统计网页数（Top 10）
    top_websites = (
        db.query(Website.domain, func.count(Webpage.id).label("count"))
        .join(Webpage, Website.id == Webpage.website_id, isouter=True)
        .group_by(Website.id, Website.domain)
        .order_by(func.count(Webpage.id).desc())
        .limit(10)
        .all()
    )

    return success({
        "tasks": {
            "total": task_total,
            "running": task_running,
            "completed": task_completed,
            "failed": task_failed,
        },
        "websites": website_total,
        "webpages": webpage_total,
        "contents": content_total,
        "images": image_total,
        "top_websites": [
            {"domain": row.domain, "webpage_count": row.count}
            for row in top_websites
        ],
    })
