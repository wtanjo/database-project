from typing import Any

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
