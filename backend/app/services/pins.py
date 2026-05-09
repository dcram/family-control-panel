import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.kiosk_pin import KioskPin


def get_pin(db: Session, holder_type: str, holder_id: uuid.UUID) -> KioskPin | None:
    return db.scalar(
        select(KioskPin).where(
            KioskPin.holder_type == holder_type,
            KioskPin.holder_id == holder_id,
        )
    )


def upsert_pin(
    db: Session, holder_type: str, holder_id: uuid.UUID, new_pin: str
) -> KioskPin:
    current = get_pin(db=db, holder_type=holder_type, holder_id=holder_id)

    if current and current.pin == new_pin:
        return current

    taken_by = db.get(entity=KioskPin, ident=new_pin)
    if taken_by and taken_by.holder_id != holder_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Le PIN {new_pin} est déjà attribué à quelqu'un d'autre.",
        )

    if current:
        db.delete(current)
        db.flush()

    pin = KioskPin(pin=new_pin, holder_type=holder_type, holder_id=holder_id)
    db.add(instance=pin)
    db.commit()
    db.refresh(instance=pin)
    return pin
