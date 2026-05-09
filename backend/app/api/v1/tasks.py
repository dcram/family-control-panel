import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_parent
from app.core.database import get_db
from app.models.assignment import Assignment
from app.models.parent import Parent
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task_or_404(task_id: uuid.UUID, db: Session) -> Task:
    task = db.get(entity=Task, ident=task_id)
    if not task or task.archived_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tâche introuvable")
    return task


@router.get("/")
def list_tasks(
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> list[TaskOut]:
    rows = db.scalars(select(Task).where(Task.archived_at.is_(None))).all()
    return [TaskOut.model_validate(obj=r) for r in rows]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> TaskOut:
    task = Task(
        label=body.label,
        emoji=body.emoji,
        min_age=body.min_age,
        duration_minutes=body.duration_minutes,
    )
    db.add(instance=task)
    db.commit()
    db.refresh(instance=task)
    return TaskOut.model_validate(obj=task)


@router.put("/{task_id}")
def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> TaskOut:
    task = _get_task_or_404(task_id=task_id, db=db)
    if body.label is not None:
        task.label = body.label
    if body.emoji is not None:
        task.emoji = body.emoji
    if body.min_age is not None:
        task.min_age = body.min_age
    if body.duration_minutes is not None:
        task.duration_minutes = body.duration_minutes
    db.commit()
    db.refresh(instance=task)
    return TaskOut.model_validate(obj=task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> None:
    task = _get_task_or_404(task_id=task_id, db=db)
    db.execute(delete(Assignment).where(Assignment.task_id == task_id))
    task.archived_at = datetime.now(tz=timezone.utc)
    db.commit()
