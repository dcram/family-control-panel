from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_parent
from app.core.database import get_db
from app.models.assignment import Assignment
from app.models.parent import Parent
from app.models.task_instance import TaskInstance
from app.schemas.instance import InstanceOut
from app.services.instances import (
    apply_30h_transitions,
    build_instance,
    get_current_week_start,
    get_next_week_start,
    is_week_materialized,
)

router = APIRouter(prefix="/instances", tags=["instances"])


@router.get("/week/{week_start}")
def get_week_instances(
    week_start: date,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> list[InstanceOut]:
    if week_start.weekday() != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="week_start doit être un lundi (ISO : YYYY-MM-DD).",
        )

    current_week = get_current_week_start()
    next_week = get_next_week_start()

    if week_start > next_week:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation limitée à la semaine en cours + 1 (S+1).",
        )

    if week_start >= current_week and not is_week_materialized(db=db, week_start=week_start):
        assignments = db.scalars(select(Assignment)).all()
        for assignment in assignments:
            db.add(instance=build_instance(db=db, assignment=assignment, week_start=week_start))
        db.flush()

    instances = list(
        db.scalars(
            select(TaskInstance)
            .where(TaskInstance.week_start == week_start)
            .order_by(TaskInstance.day_of_week, TaskInstance.moment_label)
        ).all()
    )

    apply_30h_transitions(db=db, instances=instances)
    db.commit()

    return [InstanceOut.model_validate(obj=i) for i in instances]
