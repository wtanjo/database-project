import os
import subprocess
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.mysql import get_db
from models.task import Task
# from schemas.task import TaskCreate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("")
async def create_task(url_data: dict, db: Session = Depends(get_db)):
    """
    1. Accept the url from the frontend
    2. Log this task in MySQL
    3. Start Scrapy with subprocess
    """
    
    target_url = url_data.get("url")
    if not target_url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    new_task = Task(task_url=target_url, task_status="pending", task_id=100)
    # db.add(new_task)
    # db.commit()
    # db.refresh(new_task)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    crawler_cwd = os.path.join(current_dir, "../crawler")

    try:
        subprocess.Popen(
            [
                "scrapy", "crawl", "crwaler",
                "-a", f"start_url={target_url}",
                "-a", f"task_id={task_id}"
            ],
            cwd=crawler_cwd
        )
    except Exception as e:
        return {"status": "error", "message": f"Failed to start the crawler: {str(e)}"}

    return {
        "status": "success",
        "task_id": task_id,
        "message": "Crawler started!"
    }
