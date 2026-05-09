import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class KioskPin(Base):
    __tablename__ = "kiosk_pins"
    __table_args__ = (
        sa.UniqueConstraint("holder_type", "holder_id", name="uq_kiosk_pins_holder"),
        sa.CheckConstraint(
            "holder_type IN ('parent', 'child')", name="ck_kiosk_pins_holder_type"
        ),
    )

    pin: Mapped[str] = mapped_column(sa.CHAR(4), primary_key=True)
    holder_type: Mapped[str] = mapped_column(sa.String(10))
    holder_id: Mapped[uuid.UUID] = mapped_column(sa.Uuid(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        server_default=sa.text("NOW()"),
    )
