from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from db.mysql import get_db
from models.CrawlTask import CrawlTask
from models.Website import Website
from models.Webpage import Webpage
from models.Image import Image
from utils import success

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
def get_stats(db: Session = Depends(get_db)):
    """返回系统整体统计数据——全部从 MySQL 查询"""
    task_total = db.query(func.count(CrawlTask.id)).scalar()
    task_running = (
        db.query(func.count(CrawlTask.id))
        .filter(CrawlTask.status == "running")
        .scalar()
    )
    task_completed = (
        db.query(func.count(CrawlTask.id))
        .filter(CrawlTask.status == "completed")
        .scalar()
    )
    task_failed = (
        db.query(func.count(CrawlTask.id))
        .filter(CrawlTask.status == "failed")
        .scalar()
    )

    website_total = db.query(func.count(Website.id)).scalar()
    webpage_total = db.query(func.count(Webpage.id)).scalar()

    # 有正文的网页数（替代 MongoDB contents_collection.count）
    content_total = (
        db.query(func.count(Webpage.id))
        .filter(Webpage.text_content.isnot(None))
        .scalar()
    )
    # 图片总数（替代 MongoDB images_collection.count）
    image_total = db.query(func.count(Image.id)).scalar()

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
            {"domain": row.domain, "webpage_count": row.count} for row in top_websites
        ],
    })
