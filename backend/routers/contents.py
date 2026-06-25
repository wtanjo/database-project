import csv
import io
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.mysql import get_db
from models.Webpage import Webpage
from models.Image import Image
from utils import success, paginate

router = APIRouter(prefix="/api/contents", tags=["contents"])


def _build_webpage_query(
    db: Session,
    keyword: Optional[str] = None,
    webpage_url: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
):
    """构建 MySQL Webpage 查询（替代 MongoDB），按爬取时间倒序"""
    query = db.query(Webpage).filter(Webpage.text_content.isnot(None))

    if keyword:
        query = query.filter(Webpage.text_content.like(f"%{keyword}%"))
    if webpage_url:
        query = query.filter(Webpage.url.like(f"%{webpage_url}%"))
    if start_time:
        query = query.filter(Webpage.crawl_time >= start_time)
    if end_time:
        query = query.filter(Webpage.crawl_time <= f"{end_time} 23:59:59")

    return query.order_by(Webpage.crawl_time.desc())


def _batch_fetch_images(db: Session, webpage_ids: list[int]) -> dict[int, list[str]]:
    """批量获取图片 URL，按 webpage_id 分组"""
    if not webpage_ids:
        return {}
    rows = (
        db.query(Image.webpage_id, Image.image_url)
        .filter(Image.webpage_id.in_(webpage_ids))
        .all()
    )
    images_map: dict[int, list[str]] = {}
    for wid, url in rows:
        images_map.setdefault(wid, []).append(url)
    return images_map


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
    """检索内容列表——所有查询均在 MySQL 完成"""
    query = _build_webpage_query(db, keyword, webpage_url, start_time, end_time)
    total = query.count()
    webpages = query.offset((page - 1) * page_size).limit(page_size).all()

    # 批量获取图片
    wids = [wp.id for wp in webpages]
    images_map = _batch_fetch_images(db, wids)

    items = []
    for wp in webpages:
        items.append(
            {
                "webpage_id": wp.id,
                "title": wp.title or "",
                "url": wp.url,
                "text_content": wp.text_content or "",
                "keywords": [],  # 暂未实现关键词提取
                "images": images_map.get(wp.id, []),
                "crawl_time": wp.crawl_time.isoformat() + 'Z' if wp.crawl_time else "",
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
    """将检索结果导出为 CSV 文件——全部从 MySQL 查询"""
    query = _build_webpage_query(db, keyword, webpage_url, start_time, end_time)
    webpages = query.limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["webpage_id", "title", "url", "text_preview", "crawl_time"])

    for wp in webpages:
        writer.writerow(
            [
                wp.id,
                wp.title or "",
                wp.url,
                (wp.text_preview or "")[:500],
                wp.crawl_time.isoformat() + 'Z' if wp.crawl_time else "",
            ]
        )

    output.seek(0)
    filename = f"contents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
