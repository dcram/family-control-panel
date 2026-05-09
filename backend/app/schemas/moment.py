import uuid
from datetime import time

from pydantic import BaseModel


class MomentUpdate(BaseModel):
    start_time: time | None = None
    end_time: time | None = None


class MomentOut(BaseModel):
    id: uuid.UUID
    label: str
    start_time: time
    end_time: time
    sort_order: int

    model_config = {"from_attributes": True}
