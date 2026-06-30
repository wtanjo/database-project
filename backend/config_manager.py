import json
import os
import threading
from datetime import datetime, timezone

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crawler_config.json")

DEFAULTS = {
    "download_delay": 1.0,
    "depth_limit": 2,
    "closespider_pagecount": 100,
    "log_level": "WARNING",
}

_lock = threading.Lock()


def _ensure_config_file():
    if not os.path.exists(CONFIG_FILE):
        _write(DEFAULTS)


def _read():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def _write(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_config() -> dict:
    """获取当前配置，文件不存在时自动创建默认配置。"""
    _ensure_config_file()
    with _lock:
        return _read()


def save_config(data: dict):
    """保存配置并返回完整配置。仅更新传入的字段。"""
    _ensure_config_file()
    with _lock:
        current = _read()
        current.update(data)
        current["updated_at"] = datetime.now(timezone.utc).isoformat()
        _write(current)
        return current
