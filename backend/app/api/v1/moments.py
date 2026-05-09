import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_parent
from app.core.database import get_db
from app.models.moment import Moment
from app.models.parent import Parent
from app.schemas.moment import MomentOut, MomentUpdate

router = APIRouter(prefix="/moments", tags=["moments"])


def _get_moment_or_404(moment_id: uuid.UUID, db: Session) -> Moment:
    moment = db.get(entity=Moment, ident=moment_id)
    if not moment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moment introuvable")
    return moment


@router.get("/")
def list_moments(db: Session = Depends(get_db)) -> list[MomentOut]:
    rows = db.scalars(select(Moment).order_by(Moment.sort_order)).all()
    return [MomentOut.model_validate(obj=r) for r in rows]


@router.put("/{moment_id}")
def update_moment(
    moment_id: uuid.UUID,
    body: MomentUpdate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> MomentOut:
    moment = _get_moment_or_404(moment_id=moment_id, db=db)
    if body.start_time is not None:
        moment.start_time = body.start_time
    if body.end_time is not None:
        moment.end_time = body.end_time
    db.commit()
    db.refresh(instance=moment)
    return MomentOut.model_validate(obj=moment)
