import os
import time
import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="TaskFlow Task Service", version="1.0.0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskflow:taskflow@postgres:5432/taskflow")

class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    category: str = Field(min_length=2, max_length=60)

class TaskUpdate(BaseModel):
    completed: bool

def get_connection():
    return psycopg.connect(DATABASE_URL)

def initialize_database():
    last_error = None
    for _ in range(30):
        try:
            with get_connection() as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(150) NOT NULL,
                    category VARCHAR(60) NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )""")
                conn.commit()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"Database did not become ready: {last_error}")

@app.on_event("startup")
def startup():
    initialize_database()

@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "service": "task-service"}
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    with get_connection() as conn:
        row = conn.execute("""INSERT INTO tasks (title, category) VALUES (%s, %s)
            RETURNING id, title, category, completed, created_at""", (task.title, task.category)).fetchone()
        conn.commit()
    return {"id": row[0], "title": row[1], "category": row[2], "completed": row[3], "created_at": row[4]}

@app.get("/tasks")
def list_tasks():
    with get_connection() as conn:
        rows = conn.execute("""SELECT id, title, category, completed, created_at FROM tasks ORDER BY id DESC""").fetchall()
    return [{"id": r[0], "title": r[1], "category": r[2], "completed": r[3], "created_at": r[4]} for r in rows]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_connection() as conn:
        row = conn.execute("""SELECT id, title, category, completed, created_at FROM tasks WHERE id=%s""", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="task not found")
    return {"id": row[0], "title": row[1], "category": row[2], "completed": row[3], "created_at": row[4]}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    with get_connection() as conn:
        row = conn.execute("""UPDATE tasks SET completed=%s WHERE id=%s RETURNING id, title, category, completed, created_at""",
            (update.completed, task_id)).fetchone()
        conn.commit()
    if not row:
        raise HTTPException(status_code=404, detail="task not found")
    return {"id": row[0], "title": row[1], "category": row[2], "completed": row[3], "created_at": row[4]}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_connection() as conn:
        row = conn.execute("DELETE FROM tasks WHERE id=%s RETURNING id", (task_id,)).fetchone()
        conn.commit()
    if not row:
        raise HTTPException(status_code=404, detail="task not found")
    return {"message": "task deleted", "id": row[0]}
