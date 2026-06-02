from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.mysql import get_db
from models.Image import Image
from models.Webpage import Webpage
from utils import success, paginate

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("")
def list_images(
    keyword: Optional[str] = Query(None, description="图片描述关键字"),
    webpage_url: Optional[str] = Query(None, description="来源页面 URL（模糊匹配）"),
    start_time: Optional[str] = Query(None, description="爬取起始时间 YYYY-MM-DD"),
    end_time: Optional[str] = Query(None, description="爬取截止时间 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """图片列表——通过 MySQL Image 表查询"""
    query = db.query(Image)

    # 按来源页面 URL 过滤：先查 Webpage ID，再过滤 Image
    if webpage_url:
        wp_ids = (
            db.query(Webpage.id).filter(Webpage.url.like(f"%{webpage_url}%")).subquery()
        )
        query = query.filter(Image.webpage_id.in_(wp_ids))

    if keyword:
        query = query.filter(Image.description.like(f"%{keyword}%"))
    if start_time:
        query = query.filter(Image.crawl_time >= start_time)
    if end_time:
        query = query.filter(Image.crawl_time <= f"{end_time} 23:59:59")

    query = query.order_by(Image.crawl_time.desc())
    total = query.count()
    images = query.offset((page - 1) * page_size).limit(page_size).all()

    # 批量获取 webpage_url
    wids = [img.webpage_id for img in images]
    wps = {}
    if wids:
        rows = db.query(Webpage.id, Webpage.url).filter(Webpage.id.in_(wids)).all()
        wps = {r[0]: r[1] for r in rows}

    items = []
    for img in images:
        items.append(
            {
                "id": img.id,
                "webpage_url": wps.get(img.webpage_id, ""),
                "image_url": img.image_url,
                "description": img.description or "",
                "crawl_time": img.crawl_time.isoformat() if img.crawl_time else "",
            }
        )

    return success(paginate(items, total, page, page_size))
