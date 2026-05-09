import uuid
from datetime import time

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Moment(Base):
    __tablename__ = "moments"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    label: Mapped[str] = mapped_column(sa.String(20))
    start_time: Mapped[time] = mapped_column(sa.Time)
    end_time: Mapped[time] = mapped_column(sa.Time)
    sort_order: Mapped[int] = mapped_column(sa.Integer)
