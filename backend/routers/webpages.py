from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.mysql import get_db
from db.mongo import contents_collection, images_collection
from models.Webpage import Webpage
from models.Website import Website
from utils import success, error, paginate

router = APIRouter(prefix="/api/webpages", tags=["webpages"])


@router.get("")
def list_webpages(
    website_id: Optional[int] = Query(None, description="按网站 ID 过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取网页列表，可按所属网站过滤，分页返回。"""
    query = db.query(Webpage).order_by(Webpage.crawl_time.desc())
    if website_id is not None:
        query = query.filter(Webpage.website_id == website_id)

    total = query.count()
    webpages = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for wp in webpages:
        website = db.query(Website).filter(Website.id == wp.website_id).first()
        items.append({
            "id": wp.id,
            "url": wp.url,
            "title": wp.title or "",
            "website_id": wp.website_id,
            "domain": website.domain if website else "",
            "crawl_time": wp.crawl_time.isoformat() if wp.crawl_time else None,
            "status": wp.status,
        })

    return success(paginate(items, total, page, page_size))


@router.delete("/{webpage_id}")
def delete_webpage(webpage_id: int, db: Session = Depends(get_db)):
    """删除网页及其在 MongoDB 中关联的内容和图片（级联删除）。"""
    webpage = db.query(Webpage).filter(Webpage.id == webpage_id).first()
    if not webpage:
        raise HTTPException(status_code=404, detail="网页不存在")

    url = webpage.url

    # 先删 MongoDB 数据，再删 MySQL
    contents_collection.delete_many({"webpage_url": url})
    images_collection.delete_many({"webpage_url": url})

    db.delete(webpage)
    db.commit()

    return success(message="删除成功")
