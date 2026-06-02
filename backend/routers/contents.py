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
from utils import build_mongo_filter, success, paginate

router = APIRouter(prefix="/api/contents", tags=["contents"])


@router.get("")
def list_contents(
    keyword: Optional[str] = Query(None, description="正文关键字"),
    webpage_url: Optional[str] = Query(None, description="来源页面 URL（模糊匹配）"),
    start_time: Optional[str] = Query(None, description="爬取起始时间 YYYY-MM-DD"),
    end_time: Optional[str] = Query(None, description="爬取截止时间 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """检索内容列表，整合 MySQL 网页元信息与 MongoDB 正文/图片。"""
    mongo_filter = build_mongo_filter(keyword, start_time, end_time, webpage_url)

    total = contents_collection.count_documents(mongo_filter)
    cursor = (
        contents_collection.find(mongo_filter)
        .sort("_id", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    docs = list(cursor)
    urls = [doc.get("webpage_url", "") for doc in docs]

    # 批量查询 MySQL——一次查询代替 N 次
    webpages = {}
    if urls:
        results = db.query(Webpage).filter(Webpage.url.in_(urls)).all()
        webpages = {wp.url: wp for wp in results}

    # 批量查询 MongoDB 图片——一次查询代替 N 次
    images_map = {}
    if urls:
        img_docs = images_collection.find(
            {"webpage_url": {"$in": urls}}, {"webpage_url": 1, "image_url": 1}
        )
        for d in img_docs:
            images_map.setdefault(d["webpage_url"], []).append(d["image_url"])

    items = []
    for doc in docs:
        url = doc.get("webpage_url", "")
        webpage = webpages.get(url)

        items.append(
            {
                "webpage_id": webpage.id if webpage else None,
                "title": webpage.title if webpage else "",
                "url": url,
                "text_content": doc.get("text_content", ""),
                "keywords": doc.get("keywords", []),
                "images": images_map.get(url, []),
                "crawl_time": doc.get("crawl_time", ""),
            }
        )

    return success(paginate(items, total, page, page_size))


@router.get("/export/csv")
def export_csv(
    keyword: Optional[str] = Query(None),
    webpage_url: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """将检索结果导出为 CSV 文件。"""
    mongo_filter = build_mongo_filter(keyword, start_time, end_time, webpage_url)
    cursor = contents_collection.find(mongo_filter).sort("_id", -1).limit(5000)

    docs = list(cursor)
    urls = [doc.get("webpage_url", "") for doc in docs]

    # 批量查询 MySQL——一次查询代替 N 次
    webpages = {}
    if urls:
        results = db.query(Webpage).filter(Webpage.url.in_(urls)).all()
        webpages = {wp.url: wp for wp in results}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["webpage_id", "title", "url", "text_content", "keywords", "crawl_time"]
    )

    for doc in docs:
        url = doc.get("webpage_url", "")
        webpage = webpages.get(url)
        writer.writerow(
            [
                webpage.id if webpage else "",
                webpage.title if webpage else "",
                url,
                doc.get("text_content", "")[:500],
                ",".join(doc.get("keywords", [])),
                doc.get("crawl_time", ""),
            ]
        )

    output.seek(0)
    filename = f"contents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
