import uuid
from datetime import date, datetime

from pydantic import BaseModel


class AssignmentCreate(BaseModel):
    task_id: uuid.UUID
    child_id: uuid.UUID
    moment_id: uuid.UUID
    day_of_week: int


class AssignmentUpdate(BaseModel):
    task_id: uuid.UUID | None = None
    child_id: uuid.UUID | None = None
    moment_id: uuid.UUID | None = None
    day_of_week: int | None = None


class AssignmentOut(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    child_id: uuid.UUID
    moment_id: uuid.UUID
    day_of_week: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CloneRequest(BaseModel):
    source_week: date
    target_week: date
    overwrite: bool = False


class CloneOut(BaseModel):
    created: int
    skipped: int
