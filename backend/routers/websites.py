from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.mysql import get_db
from models.Website import Website
from utils import success, paginate

router = APIRouter(prefix="/api/websites", tags=["websites"])


@router.get("")
def list_websites(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取已爬取的网站列表。"""
    query = db.query(Website).order_by(Website.created_at.desc())
    total = query.count()
    websites = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [
        {
            "id": w.id,
            "domain": w.domain,
            "organization": w.organization or "",
            "contact": w.contact or "",
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in websites
    ]
    return success(paginate(items, total, page, page_size))
