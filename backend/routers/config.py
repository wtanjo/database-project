from fastapi import APIRouter
from config_manager import load_config, save_config
from utils import success, error

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
def get_config():
    return success(load_config())


@router.put("")
def update_config(data: dict):
    valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    if "download_delay" in data:
        delay = float(data["download_delay"])
        if delay < 0:
            return error("请求间隔不能为负数")
    if "depth_limit" in data:
        depth = int(data["depth_limit"])
        if depth < 0:
            return error("爬取深度不能为负数")
    if "closespider_pagecount" in data:
        pagecount = int(data["closespider_pagecount"])
        if pagecount < 1:
            return error("单次最大页数必须大于 0")
    if "log_level" in data:
        level = str(data["log_level"]).upper()
        if level not in valid_log_levels:
            return error(f"无效的日志级别，可选值: {', '.join(sorted(valid_log_levels))}")

    allowed = {"download_delay", "depth_limit", "closespider_pagecount", "log_level"}
    updates = {k: data[k] for k in data if k in allowed}

    if not updates:
        return error("未提供有效的配置字段")

    config = save_config(updates)
    return success(config, message="配置更新成功")
