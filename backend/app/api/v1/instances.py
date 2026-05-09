import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_parent, get_optional_parent
from app.core.database import get_db
from app.models.assignment import Assignment
from app.models.kiosk_pin import KioskPin
from app.models.parent import Parent
from app.models.task_instance import TaskInstance
from app.models.validation import Validation
from app.schemas.instance import DeclareRequest, InstanceOut, ValidateRequest
from app.services.instances import (
    apply_30h_transitions,
    build_instance,
    get_current_week_start,
    get_next_week_start,
    is_week_materialized,
)

router = APIRouter(prefix="/instances", tags=["instances"])


def _get_instance_or_404(instance_id: uuid.UUID, db: Session) -> TaskInstance:
    instance = db.get(entity=TaskInstance, ident=instance_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance introuvable")
    return instance


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


@router.post("/{instance_id}/declare")
def declare_instance(
    instance_id: uuid.UUID,
    body: DeclareRequest,
    db: Session = Depends(get_db),
) -> InstanceOut:
    kiosk_pin = db.get(entity=KioskPin, ident=body.pin)
    if not kiosk_pin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="PIN inconnu")

    if kiosk_pin.holder_type == "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PIN parent — utilisez /validate pour valider.",
        )

    instance = _get_instance_or_404(instance_id=instance_id, db=db)

    if instance.assignment_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible de déclarer : l'assignation source a été supprimée.",
        )

    assignment = db.get(entity=Assignment, ident=instance.assignment_id)
    if not assignment or kiosk_pin.holder_id != assignment.child_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce n'est pas ton PIN pour cette tâche.",
        )

    if instance.state != "assigned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"État actuel '{instance.state}' — seul 'assigned' permet de déclarer.",
        )

    instance.state = "declared"
    instance.declared_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(instance=instance)
    return InstanceOut.model_validate(obj=instance)


@router.post("/{instance_id}/validate")
def validate_instance(
    instance_id: uuid.UUID,
    body: ValidateRequest,
    db: Session = Depends(get_db),
    optional_parent: Parent | None = Depends(get_optional_parent),
) -> InstanceOut:
    parent: Parent | None = None

    if body.pin:
        kiosk_pin = db.get(entity=KioskPin, ident=body.pin)
        if not kiosk_pin or kiosk_pin.holder_type != "parent":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="PIN parent invalide.",
            )
        parent = db.get(entity=Parent, ident=kiosk_pin.holder_id)

    if parent is None:
        parent = optional_parent

    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise : PIN parent ou session admin.",
        )

    instance = _get_instance_or_404(instance_id=instance_id, db=db)

    db.execute(delete(Validation).where(Validation.instance_id == instance_id))

    validation = Validation(
        instance_id=instance_id,
        parent_id=parent.id,
        target_state=body.target_state,
        reason=body.reason,
    )
    db.add(instance=validation)

    instance.state = body.target_state
    instance.state_changed_at = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(instance=instance)
    return InstanceOut.model_validate(obj=instance)


@router.post("/{instance_id}/reset")
def reset_instance(
    instance_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> InstanceOut:
    instance = _get_instance_or_404(instance_id=instance_id, db=db)

    db.execute(delete(Validation).where(Validation.instance_id == instance_id))

    instance.state = "assigned"
    instance.declared_at = None
    instance.state_changed_at = None
    db.commit()
    db.refresh(instance=instance)
    return InstanceOut.model_validate(obj=instance)
