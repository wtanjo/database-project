from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.mysql import get_db
from db.mongo import contents_collection, images_collection
from models.Webpage import Webpage
from models.Website import Website
from utils import success, paginate

router = APIRouter(prefix="/api/webpages", tags=["webpages"])


@router.get("")
def list_webpages(
    website_id: Optional[int] = Query(None, description="按网站 ID 过滤"),
    domain: Optional[str] = Query(None, description="按域名模糊匹配"),
    url_keyword: Optional[str] = Query(None, description="按 URL 模糊匹配"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取网页列表，支持按网站 ID、域名、URL 关键字过滤，分页返回。"""
    query = db.query(Webpage).join(Website, Website.id == Webpage.website_id, isouter=True)

    if website_id is not None:
        query = query.filter(Webpage.website_id == website_id)
    if domain:
        query = query.filter(Website.domain.like(f"%{domain}%"))
    if url_keyword:
        query = query.filter(Webpage.url.like(f"%{url_keyword}%"))

    query = query.order_by(Webpage.crawl_time.desc())
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


@router.get("/{webpage_id}/detail")
def get_webpage_detail(webpage_id: int, db: Session = Depends(get_db)):
    """获取指定网页的 contents 和 images（从 MongoDB）。"""
    webpage = db.query(Webpage).filter(Webpage.id == webpage_id).first()
    if not webpage:
        raise HTTPException(status_code=404, detail="网页不存在")

    url = webpage.url

    content_doc = contents_collection.find_one({"webpage_url": url})
    content = None
    if content_doc:
        content = {
            "text_content": content_doc.get("text_content", ""),
            "keywords": content_doc.get("keywords", []),
            "crawl_time": content_doc.get("crawl_time", ""),
        }

    image_docs = images_collection.find({"webpage_url": url})
    images = [
        {
            "image_url": d.get("image_url", ""),
            "description": d.get("description", ""),
        }
        for d in image_docs
    ]

    return success({
        "id": webpage.id,
        "url": url,
        "title": webpage.title or "",
        "crawl_time": webpage.crawl_time.isoformat() if webpage.crawl_time else None,
        "content": content,
        "images": images,
    })


@router.delete("/{webpage_id}")
def delete_webpage(webpage_id: int, db: Session = Depends(get_db)):
    """删除网页及其在 MongoDB 中关联的内容和图片（级联删除）。"""
    webpage = db.query(Webpage).filter(Webpage.id == webpage_id).first()
    if not webpage:
        raise HTTPException(status_code=404, detail="网页不存在")

    url = webpage.url
    contents_collection.delete_many({"webpage_url": url})
    images_collection.delete_many({"webpage_url": url})

    db.delete(webpage)
    db.commit()

    return success(message="删除成功")
