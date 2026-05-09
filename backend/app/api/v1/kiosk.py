from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.kiosk_config import KioskConfig
from app.schemas.instance import InstanceOut
from app.schemas.kiosk import KioskInfoOut
from app.services.instances import (
    TZ_PARIS,
    get_next_week_start,
    load_week_instances,
)
from datetime import date

router = APIRouter(prefix="/kiosk", tags=["kiosk"])


@router.get("/info")
def get_kiosk_info(db: Session = Depends(get_db)) -> KioskInfoOut:
    config = db.get(entity=KioskConfig, ident=1)
    today = datetime.now(tz=TZ_PARIS).date()
    return KioskInfoOut(
        date=today,
        saint=None,
        weather=None,
        quote_text=config.quote_text if config else None,
        quote_author=config.quote_author if config else None,
        quote_work=config.quote_work if config else None,
    )


@router.get("/week/{week_start}")
def get_kiosk_week(
    week_start: date,
    db: Session = Depends(get_db),
) -> list[InstanceOut]:
    if week_start.weekday() != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_start doit être un lundi (ISO : YYYY-MM-DD).",
        )
    if week_start > get_next_week_start():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation limitée à la semaine en cours + 1 (S+1).",
        )
    instances = load_week_instances(db=db, week_start=week_start)
    return [InstanceOut.model_validate(obj=i) for i in instances]
