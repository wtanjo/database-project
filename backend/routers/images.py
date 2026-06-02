from typing import Optional
from fastapi import APIRouter, Query
from db.mongo import images_collection
from utils import build_mongo_filter, success, paginate

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("")
def list_images(
    keyword: Optional[str] = Query(None, description="图片描述关键字"),
    webpage_url: Optional[str] = Query(None, description="来源页面 URL（模糊匹配）"),
    start_time: Optional[str] = Query(None, description="爬取起始时间 YYYY-MM-DD"),
    end_time: Optional[str] = Query(None, description="爬取截止时间 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """图片列表，支持按描述关键字、来源 URL、爬取时间过滤，分页返回。"""
    # 使用共享过滤器构建器；图片的 keyword 字段是 description，需要手动替换
    mongo_filter = build_mongo_filter(
        start_time=start_time,
        end_time=end_time,
        webpage_url=webpage_url,
    )
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
