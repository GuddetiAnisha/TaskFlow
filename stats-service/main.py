import os
import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(title="TaskFlow Statistics Service", version="1.0.0")
TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://task-service:8000")

@app.get("/health")
def health():
    return {"status": "ok", "service": "stats-service"}

@app.get("/stats")
def stats():
    try:
        response = httpx.get(f"{TASK_SERVICE_URL}/tasks", timeout=5.0)
        response.raise_for_status()
        tasks = response.json()
    except Exception:
        raise HTTPException(status_code=503, detail="task service unavailable")

    total = len(tasks)
    completed = sum(1 for task in tasks if task["completed"])
    categories = {}
    for task in tasks:
        categories[task["category"]] = categories.get(task["category"], 0) + 1

    return {"total": total, "completed": completed, "pending": total - completed, "categories": categories}
