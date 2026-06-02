import os
import subprocess
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.mysql import get_db
from models.CrawlTask import CrawlTask
from utils import success, error, paginate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _validate_url(url: str) -> str:
    """验证 URL 格式：必须有 http/https scheme 和有效 netloc"""
    url = url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL 不能为空")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="仅支持 http/https 协议的 URL")
    if not parsed.netloc:
        raise HTTPException(status_code=400, detail="URL 格式无效，缺少域名")
    if len(url) > 2048:
        raise HTTPException(status_code=400, detail="URL 长度不能超过 2048 字符")
    return url


@router.post("")
async def create_task(url_data: dict, db: Session = Depends(get_db)):
    """提交爬取任务，写入 MySQL 后异步触发 Scrapy。"""
    # 兼容 target_url / url 两种字段名
    raw_url = url_data.get("target_url") or url_data.get("url") or ""
    url = _validate_url(str(raw_url))

    new_task = CrawlTask(target_url=url, status=CrawlTask.Status.PENDING)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    crawler_cwd = os.path.join(current_dir, "../crawler")

    try:
        subprocess.Popen(
            [
                "scrapy", "crawl", "crawler",
                "-a", f"start_url={new_task.target_url}",
                "-a", f"task_id={new_task.id}",
            ],
            cwd=crawler_cwd,
        )
    except Exception as e:
        return error(f"爬虫启动失败: {str(e)}")

    return success(
        {"task_id": new_task.id, "status": new_task.status},
        message="任务创建成功",
    )


@router.get("")
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """分页获取任务列表。"""
    query = db.query(CrawlTask).order_by(CrawlTask.created_at.desc())
    total = query.count()
    tasks = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [
        {
            "id": t.id,
            "target_url": t.target_url,
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "finished_at": t.finished_at.isoformat() if t.finished_at else None,
            "page_count": t.page_count,
            "error_msg": t.error_msg or "",
        }
        for t in tasks
    ]
    return success(paginate(items, total, page, page_size))
