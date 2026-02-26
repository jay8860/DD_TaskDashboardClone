from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
import os

router = APIRouter()

# --- Schemas ---
class TaskCreate(BaseModel):
    task_number: Optional[str] = None
    description: Optional[str] = None
    assigned_agency: Optional[str] = None
    priority: Optional[str] = None
    allocated_date: Optional[date] = None
    deadline_date: Optional[date] = None
    status: Optional[str] = "Pending"
    remarks: Optional[str] = None
    deadline_due_in: Optional[str] = None
    time_given: Optional[str] = None
    is_pinned: Optional[bool] = False
    scheduled_date: Optional[date] = None
    attachment_data: Optional[str] = None

class TaskUpdate(BaseModel):
    task_number: Optional[str] = None
    description: Optional[str] = None
    assigned_agency: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None
    completion_date: Optional[str] = None
    deadline_due_in: Optional[str] = None
    time_given: Optional[str] = None
    deadline_date: Optional[date] = None
    is_pinned: Optional[bool] = None
    scheduled_date: Optional[date] = None
    priority: Optional[str] = None

class TaskBulkUpdateItem(BaseModel):
    id: int
    task_number: Optional[str] = None
    description: Optional[str] = None
    assigned_agency: Optional[str] = None
    priority: Optional[str] = None
    allocated_date: Optional[date] = None
    deadline_date: Optional[date] = None
    status: Optional[str] = None
    remarks: Optional[str] = None
    deadline_due_in: Optional[str] = None
    time_given: Optional[str] = None
    is_pinned: Optional[bool] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[str] = None
    completion_date: Optional[str] = None

class TaskBulkUpdateList(BaseModel):
    updates: List[TaskBulkUpdateItem]

# --- Helper ---
def sync_task_status(task):
    if task.completion_date and str(task.completion_date).strip():
        task.status = "Completed"
    else:
        if task.deadline_date and task.deadline_date < date.today():
            task.status = "Overdue"
        else:
            task.status = "Pending"

def refresh_all_task_statuses(db: Session):
    """Updates status for all non-completed tasks based on today's date."""
    tasks_to_refresh = db.query(models.Task).filter(models.Task.status.in_(["Pending", "Overdue"])).all()
    for task in tasks_to_refresh:
        sync_task_status(task)

# --- Routes ---

@router.get("/")
def get_tasks(
    agency: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "deadline_date",
    db: Session = Depends(get_db)
):
    refresh_all_task_statuses(db)
    db.commit()
    query = db.query(models.Task)

    if agency:
        if ',' in agency:
            agency_list = [a.strip() for a in agency.split(',')]
            query = query.filter(models.Task.assigned_agency.in_(agency_list))
        else:
            query = query.filter(models.Task.assigned_agency == agency)

    if status:
        if ',' in status:
            status_list = [s.strip() for s in status.split(',')]
            query = query.filter(models.Task.status.in_(status_list))
        else:
            query = query.filter(models.Task.status == status)

    if search:
        query = query.filter(
            models.Task.description.contains(search) | models.Task.task_number.contains(search)
        )

    if sort_by == "deadline_date":
        query = query.order_by(models.Task.deadline_date.asc())

    return query.all()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    refresh_all_task_statuses(db)
    db.commit()
    total = db.query(models.Task).count()
    completed = db.query(models.Task).filter(models.Task.status == "Completed").count()
    overdue = db.query(models.Task).filter(models.Task.status == "Overdue").count()
    pending = total - completed

    from sqlalchemy import func
    agency_stats = db.query(models.Task.assigned_agency, func.count(models.Task.id))\
        .group_by(models.Task.assigned_agency).all()

    return {
        "total": total,
        "completed": completed,
        "overdue": overdue,
        "pending": pending,
        "by_agency": [{"name": a, "count": c} for a, c in agency_stats if a]
    }

@router.post("/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Auto-generate Task Number if missing
    if not task.task_number:
        existing_tasks = db.query(models.Task.task_number).all()
        max_num = 0
        for t in existing_tasks:
            t_num = t.task_number
            if t_num and t_num.startswith("Task "):
                try:
                    num = int(t_num.replace("Task ", ""))
                    if num > max_num:
                        max_num = num
                except:
                    pass
        task.task_number = f"Task {max_num + 1}"

    db_task = models.Task(**task.dict(), source="Manual")
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating task: {str(e)}")

@router.get("/duplicates")
def get_duplicate_tasks(db: Session = Depends(get_db)):
    all_tasks = db.query(models.Task).filter(models.Task.status != "Deleted").all()
    groups = {}
    for task in all_tasks:
        if not task.task_number:
            continue
        key = task.task_number.strip().lower()
        if key not in groups:
            groups[key] = []
        groups[key].append(task)

    duplicates = [tasks for k, tasks in groups.items() if len(tasks) > 1]
    return duplicates

@router.put("/{task_id}")
def update_task(task_id: int, update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Not Found")

    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    sync_task_status(task)
    db.commit()
    return task

@router.put("/bulk/update")
def bulk_update_tasks(bulk_data: TaskBulkUpdateList, db: Session = Depends(get_db)):
    updated_count = 0

    for update_item in bulk_data.updates:
        task = db.query(models.Task).filter(models.Task.id == update_item.id).first()
        if not task:
            continue

        update_data_dict = update_item.dict(exclude_unset=True)
        update_data_dict.pop('id', None)

        if not update_data_dict:
            continue

        for key, value in update_data_dict.items():
            setattr(task, key, value)

        sync_task_status(task)
        updated_count += 1

    db.commit()
    return {"message": f"Successfully updated {updated_count} tasks"}

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Not Found")

    db.delete(task)
    db.commit()
    return {"message": "Task Deleted"}


