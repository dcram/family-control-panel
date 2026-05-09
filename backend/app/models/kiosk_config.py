from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class KioskConfig(Base):
    __tablename__ = "kiosk_config"
    __table_args__ = (sa.CheckConstraint("id = 1", name="single_row"),)

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, default=1, server_default=sa.text("1")
    )
    weather_city: Mapped[str] = mapped_column(
        sa.String(100), default="Paris", server_default=sa.text("'Paris'")
    )
    quote_text: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    quote_author: Mapped[str | None] = mapped_column(sa.String(200), nullable=True)
    quote_work: Mapped[str | None] = mapped_column(sa.String(200), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        server_default=sa.text("NOW()"),
    )
