import uuid
from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    label: str
    emoji: str | None = None
    min_age: int = 4
    duration_minutes: int


class TaskUpdate(BaseModel):
    label: str | None = None
    emoji: str | None = None
    min_age: int | None = None
    duration_minutes: int | None = None


class TaskOut(BaseModel):
    id: uuid.UUID
    label: str
    emoji: str | None
    min_age: int
    duration_minutes: int
    archived_at: datetime | None

    model_config = {"from_attributes": True}
