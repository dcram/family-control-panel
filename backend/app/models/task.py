import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    label: Mapped[str] = mapped_column(sa.String(200))
    emoji: Mapped[str | None] = mapped_column(sa.String(10), nullable=True)
    min_age: Mapped[int] = mapped_column(
        sa.Integer, default=4, server_default=sa.text("4")
    )
    duration_minutes: Mapped[int] = mapped_column(sa.Integer)
    archived_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        server_default=sa.text("NOW()"),
    )
