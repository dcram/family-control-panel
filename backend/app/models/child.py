import uuid
from datetime import date, datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Child(Base):
    __tablename__ = "children"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    first_name: Mapped[str] = mapped_column(sa.String(100))
    date_of_birth: Mapped[date] = mapped_column(sa.Date)
    color: Mapped[str] = mapped_column(sa.String(20))
    sort_order: Mapped[int] = mapped_column(
        sa.Integer, default=0, server_default=sa.text("0")
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        server_default=sa.text("NOW()"),
    )
