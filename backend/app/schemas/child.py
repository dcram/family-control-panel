import uuid
from datetime import date, datetime

from pydantic import BaseModel

CHILD_COLORS = ["green", "blue", "amber", "coral", "purple", "gray"]


class ChildCreate(BaseModel):
    first_name: str
    date_of_birth: date


class ChildUpdate(BaseModel):
    first_name: str | None = None
    date_of_birth: date | None = None


class ChildOut(BaseModel):
    id: uuid.UUID
    first_name: str
    date_of_birth: date
    color: str
    sort_order: int
    archived_at: datetime | None

    model_config = {"from_attributes": True}
