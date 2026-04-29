import os
import subprocess
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.mysql import get_db
from models.CrawlTask import CrawlTask
from utils import success, error, paginate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("")
async def create_task(url_data: dict, db: Session = Depends(get_db)):
    """提交爬取任务，写入 MySQL 后异步触发 Scrapy。"""
    # 兼容 target_url / url 两种字段名
    url = url_data.get("target_url") or url_data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL 不能为空")

    new_task = CrawlTask(target_url=url, status="pending")
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
