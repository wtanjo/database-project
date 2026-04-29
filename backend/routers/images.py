from typing import Optional
from fastapi import APIRouter, Query
from db.mongo import images_collection
from utils import success, paginate

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("")
def list_images(
    keyword: Optional[str] = Query(None, description="图片描述关键字"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """图片列表，支持按描述关键字过滤，分页返回。"""
    mongo_filter: dict = {}
    if keyword:
        mongo_filter["description"] = {"$regex": keyword, "$options": "i"}

    total = images_collection.count_documents(mongo_filter)
    cursor = (
        images_collection.find(mongo_filter)
        .sort("_id", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )

    items = []
    for doc in cursor:
        items.append({
            "id": str(doc["_id"]),
            "webpage_url": doc.get("webpage_url", ""),
            "image_url": doc.get("image_url", ""),
            "description": doc.get("description", ""),
            "crawl_time": doc.get("crawl_time", ""),
        })

    return success(paginate(items, total, page, page_size))
