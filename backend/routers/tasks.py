import os
import subprocess
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.mysql import get_db
from models.CrawlTask import CrawlTask
# from schemas.task import TaskCreate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("")
async def create_task(url_data: dict, db: Session = Depends(get_db)):
    """
    1. Accept the url from the frontend
    2. Log this task in MySQL
    3. Start Scrapy with subprocess
    """
    
    url = url_data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

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
                "-a", f"task_id={new_task.id}"
            ],
            cwd=crawler_cwd
        )
    except Exception as e:
        return {"status": "error", "message": f"Failed to start the crawler: {str(e)}"}

    return {
        "status": "success",
        "task_id": new_task.id,
        "message": "Crawler started!"
    }
