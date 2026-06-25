from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from db.mysql import get_db
from models.Webpage import Webpage
from models.Website import Website
from models.Image import Image
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
    website_ids = set()
    if domain:
        wids = db.query(Website.id).filter(Website.domain.like(f"%{domain}%")).all()
        website_ids = {r[0] for r in wids}
        if not website_ids:
            return success(paginate([], 0, page, page_size))

    query = db.query(Webpage)
    if website_id is not None:
        query = query.filter(Webpage.website_id == website_id)
    if website_ids:
        query = query.filter(Webpage.website_id.in_(website_ids))
    if url_keyword:
        query = query.filter(Webpage.url.like(f"%{url_keyword}%"))

    query = query.order_by(Webpage.crawl_time.desc())
    total = query.count()
    webpages = query.offset((page - 1) * page_size).limit(page_size).all()

    # 批量加载 Website
    wp_website_ids = {wp.website_id for wp in webpages if wp.website_id}
    websites = {}
    if wp_website_ids:
        results = db.query(Website).filter(Website.id.in_(wp_website_ids)).all()
        websites = {w.id: w for w in results}

    items = []
    for wp in webpages:
        website = websites.get(wp.website_id)
        items.append(
            {
                "id": wp.id,
                "url": wp.url,
                "title": wp.title or "",
                "website_id": wp.website_id,
                "domain": website.domain if website else "",
                "crawl_time": wp.crawl_time.isoformat() + 'Z' if wp.crawl_time else None,
                "status": wp.status,
            }
        )

    return success(paginate(items, total, page, page_size))


@router.get("/{webpage_id}/detail")
def get_webpage_detail(webpage_id: int, db: Session = Depends(get_db)):
    """获取指定网页的详细内容——通过 MySQL Webpage + Image 表查询"""
    webpage = db.query(Webpage).filter(Webpage.id == webpage_id).first()
    if not webpage:
        raise HTTPException(status_code=404, detail="网页不存在")

    # 正文从 Webpage 表直接读取
    content = None
    if webpage.text_content:
        content = {
            "text_content": webpage.text_content,
            "keywords": [],  # 暂未实现关键词提取
            "crawl_time": webpage.crawl_time.isoformat() + 'Z'
            if webpage.crawl_time
            else "",
        }

        # 图片从 Image 表查询
        image_rows = db.query(Image).filter(Image.webpage_id == webpage_id).all()
        images = [
            {"image_url": img.image_url, "description": img.description or ""}
            for img in image_rows
        ]

        return success(
            {
                "id": webpage.id,
                "url": webpage.url,
                "title": webpage.title or "",
                "crawl_time": webpage.crawl_time.isoformat() + 'Z'
                if webpage.crawl_time
                else None,
            "content": content,
            "images": images,
        }
    )


@router.delete("/{webpage_id}")
def delete_webpage(webpage_id: int, db: Session = Depends(get_db)):
    """删除网页及关联的图片（MySQL 级联删除 Image + MongoDB 清理）"""
    webpage = db.query(Webpage).filter(Webpage.id == webpage_id).first()
    if not webpage:
        raise HTTPException(status_code=404, detail="网页不存在")

    # MySQL 级联：Webpage → Image（ondelete=CASCADE）
    db.delete(webpage)
    db.commit()

    # MongoDB 清理（异步备份数据）
    try:
        from db.mongo import contents_collection, images_collection

        contents_collection.delete_many({"webpage_url": webpage.url})
        images_collection.delete_many({"webpage_url": webpage.url})
    except Exception:
        pass

    return success(message="删除成功")
