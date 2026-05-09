import uuid
from datetime import date, datetime

from pydantic import BaseModel


class InstanceOut(BaseModel):
    id: uuid.UUID
    assignment_id: uuid.UUID | None
    week_start: date
    instance_date: date
    state: str
    declared_at: datetime | None
    state_changed_at: datetime | None
    task_label: str
    task_emoji: str | None
    task_duration_minutes: int
    child_first_name: str
    child_color: str
    moment_label: str
    day_of_week: int

    model_config = {"from_attributes": True}
