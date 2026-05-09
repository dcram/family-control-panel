import uuid
from datetime import date, datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TaskInstance(Base):
    __tablename__ = "task_instances"
    __table_args__ = (
        sa.UniqueConstraint(
            "assignment_id", "week_start", name="uq_task_instances_assignment_week"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid(as_uuid=True),
        sa.ForeignKey("assignments.id", ondelete="SET NULL"),
        nullable=True,
    )
    week_start: Mapped[date] = mapped_column(sa.Date)
    instance_date: Mapped[date] = mapped_column(sa.Date)
    state: Mapped[str] = mapped_column(
        sa.String(20),
        default="assigned",
        server_default=sa.text("'assigned'"),
    )
    declared_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    state_changed_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    task_label: Mapped[str] = mapped_column(sa.String(200))
    task_emoji: Mapped[str | None] = mapped_column(sa.String(10), nullable=True)
    task_duration_minutes: Mapped[int] = mapped_column(sa.Integer)
    child_first_name: Mapped[str] = mapped_column(sa.String(100))
    child_color: Mapped[str] = mapped_column(sa.String(20))
    moment_label: Mapped[str] = mapped_column(sa.String(20))
    day_of_week: Mapped[int] = mapped_column(sa.Integer)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        server_default=sa.text("NOW()"),
    )
