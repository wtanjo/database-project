from typing import Any, Optional


def success(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def error(message: str = "error", code: int = 1) -> dict:
    return {"code": code, "message": message, "data": None}


def paginate(items: list, total: int, page: int, page_size: int) -> dict:
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


def iso(dt):
    """返回 ISO 8601 字符串，空值返回 None"""
    return dt.isoformat() if dt else None


def build_mongo_filter(
    keyword: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    webpage_url: Optional[str] = None,
) -> dict:
    """构建 MongoDB 查询过滤器，被 contents 和 images router 复用"""
    mongo_filter: dict = {}
    if keyword:
        mongo_filter["text_content"] = {"$regex": keyword, "$options": "i"}
    if webpage_url:
        mongo_filter["webpage_url"] = {"$regex": webpage_url, "$options": "i"}
    if start_time or end_time:
        time_filter: dict = {}
        if start_time:
            time_filter["$gte"] = start_time
        if end_time:
            time_filter["$lte"] = end_time
        mongo_filter["crawl_time"] = time_filter
    return mongo_filter
