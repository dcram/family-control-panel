from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_parent
from app.core.database import get_db
from app.models.kiosk_config import KioskConfig
from app.models.parent import Parent
from app.schemas.config import KioskConfigOut, QuoteUpdate, WeatherCityUpdate

router = APIRouter(prefix="/config", tags=["config"])


def _get_config(db: Session) -> KioskConfig:
    config = db.get(entity=KioskConfig, ident=1)
    assert config is not None
    return config


@router.get("/")
def get_config(db: Session = Depends(get_db)) -> KioskConfigOut:
    return KioskConfigOut.model_validate(obj=_get_config(db=db))


@router.put("/weather")
def update_weather(
    body: WeatherCityUpdate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> KioskConfigOut:
    config = _get_config(db=db)
    config.weather_city = body.weather_city
    config.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(instance=config)
    return KioskConfigOut.model_validate(obj=config)


@router.put("/quote")
def update_quote(
    body: QuoteUpdate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> KioskConfigOut:
    config = _get_config(db=db)
    config.quote_text = body.quote_text
    config.quote_author = body.quote_author
    config.quote_work = body.quote_work
    config.updated_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(instance=config)
    return KioskConfigOut.model_validate(obj=config)
