import csv
import io
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.mysql import get_db
from db.mongo import contents_collection, images_collection
from models.Webpage import Webpage
from utils import success, paginate

router = APIRouter(prefix="/api/contents", tags=["contents"])


def _build_mongo_filter(keyword: Optional[str], start_time: Optional[str], end_time: Optional[str]) -> dict:
    mongo_filter: dict = {}
    if keyword:
        mongo_filter["text_content"] = {"$regex": keyword, "$options": "i"}
    if start_time or end_time:
        time_filter: dict = {}
        if start_time:
            time_filter["$gte"] = start_time
        if end_time:
            time_filter["$lte"] = end_time
        mongo_filter["crawl_time"] = time_filter
    return mongo_filter


@router.get("")
def list_contents(
    keyword: Optional[str] = Query(None, description="正文关键字"),
    start_time: Optional[str] = Query(None, description="爬取起始时间 YYYY-MM-DD"),
    end_time: Optional[str] = Query(None, description="爬取截止时间 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """检索内容列表，整合 MySQL 网页元信息与 MongoDB 正文/图片。"""
    mongo_filter = _build_mongo_filter(keyword, start_time, end_time)

    total = contents_collection.count_documents(mongo_filter)
    cursor = (
        contents_collection.find(mongo_filter)
        .sort("_id", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    items = []
    for doc in cursor:
        url = doc.get("webpage_url", "")
        # 从 MySQL 补充网页元信息
        webpage = db.query(Webpage).filter(Webpage.url == url).first()
        # 从 MongoDB 拿该 URL 的图片
        img_docs = images_collection.find({"webpage_url": url}, {"image_url": 1})
        images = [d["image_url"] for d in img_docs]

        items.append({
            "webpage_id": webpage.id if webpage else None,
            "title": webpage.title if webpage else "",
            "url": url,
            "text_content": doc.get("text_content", ""),
            "keywords": doc.get("keywords", []),
            "images": images,
            "crawl_time": doc.get("crawl_time", ""),
        })

    return success(paginate(items, total, page, page_size))


@router.get("/export/csv")
def export_csv(
    keyword: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """将检索结果导出为 CSV 文件。"""
    mongo_filter = _build_mongo_filter(keyword, start_time, end_time)
    cursor = contents_collection.find(mongo_filter).sort("_id", -1).limit(5000)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["webpage_id", "title", "url", "text_content", "keywords", "crawl_time"])

    for doc in cursor:
        url = doc.get("webpage_url", "")
        webpage = db.query(Webpage).filter(Webpage.url == url).first()
        writer.writerow([
            webpage.id if webpage else "",
            webpage.title if webpage else "",
            url,
            doc.get("text_content", "")[:500],
            ",".join(doc.get("keywords", [])),
            doc.get("crawl_time", ""),
        ])

    output.seek(0)
    filename = f"contents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
