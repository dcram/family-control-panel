import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_parent
from app.core.database import get_db
from app.models.assignment import Assignment
from app.models.parent import Parent
from app.models.task_instance import TaskInstance
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentOut,
    AssignmentUpdate,
    CloneOut,
    CloneRequest,
)
from app.services.instances import (
    build_instance,
    get_current_week_start,
    get_instance_for_week,
    get_next_week_start,
    is_week_materialized,
    refresh_instance_snapshot,
)

router = APIRouter(prefix="/assignments", tags=["assignments"])


def _get_assignment_or_404(assignment_id: uuid.UUID, db: Session) -> Assignment:
    assignment = db.get(entity=Assignment, ident=assignment_id)
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignation introuvable")
    return assignment


def _check_current_week_instance(
    db: Session, assignment_id: uuid.UUID
) -> TaskInstance | None:
    instance = get_instance_for_week(
        db=db, assignment_id=assignment_id, week_start=get_current_week_start()
    )
    if instance and instance.state != "assigned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "L'instance de la semaine en cours n'est pas dans l'état 'assigned'. "
                "Réinitialisez-la d'abord via POST /instances/{id}/reset."
            ),
        )
    return instance


@router.get("/")
def list_assignments(
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> list[AssignmentOut]:
    rows = db.scalars(select(Assignment)).all()
    return [AssignmentOut.model_validate(obj=r) for r in rows]


@router.post("/clone")
def clone_week(
    body: CloneRequest,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> CloneOut:
    _validate_monday(body.source_week)
    _validate_monday(body.target_week)

    source_instances = db.scalars(
        select(TaskInstance).where(TaskInstance.week_start == body.source_week)
    ).all()

    if body.overwrite:
        db.execute(
            delete(TaskInstance).where(TaskInstance.week_start == body.target_week)
        )
        db.flush()

    created = 0
    skipped = 0
    for src in source_instances:
        if src.assignment_id is None:
            skipped += 1
            continue
        existing = get_instance_for_week(
            db=db, assignment_id=src.assignment_id, week_start=body.target_week
        )
        if existing:
            skipped += 1
            continue
        assignment = db.get(entity=Assignment, ident=src.assignment_id)
        if not assignment:
            skipped += 1
            continue
        db.add(instance=build_instance(db=db, assignment=assignment, week_start=body.target_week))
        created += 1

    db.commit()
    return CloneOut(created=created, skipped=skipped)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_assignment(
    body: AssignmentCreate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> AssignmentOut:
    assignment = Assignment(
        task_id=body.task_id,
        child_id=body.child_id,
        moment_id=body.moment_id,
        day_of_week=body.day_of_week,
    )
    db.add(instance=assignment)
    db.flush()

    for week_start in [get_current_week_start(), get_next_week_start()]:
        if is_week_materialized(db=db, week_start=week_start):
            db.add(instance=build_instance(db=db, assignment=assignment, week_start=week_start))

    db.commit()
    db.refresh(instance=assignment)
    return AssignmentOut.model_validate(obj=assignment)


@router.put("/{assignment_id}")
def update_assignment(
    assignment_id: uuid.UUID,
    body: AssignmentUpdate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> AssignmentOut:
    assignment = _get_assignment_or_404(assignment_id=assignment_id, db=db)
    current_instance = _check_current_week_instance(db=db, assignment_id=assignment_id)

    if body.task_id is not None:
        assignment.task_id = body.task_id
    if body.child_id is not None:
        assignment.child_id = body.child_id
    if body.moment_id is not None:
        assignment.moment_id = body.moment_id
    if body.day_of_week is not None:
        assignment.day_of_week = body.day_of_week

    if current_instance and current_instance.state == "assigned":
        refresh_instance_snapshot(db=db, instance=current_instance, assignment=assignment)

    db.commit()
    db.refresh(instance=assignment)
    return AssignmentOut.model_validate(obj=assignment)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> None:
    assignment = _get_assignment_or_404(assignment_id=assignment_id, db=db)
    current_instance = _check_current_week_instance(db=db, assignment_id=assignment_id)

    if current_instance and current_instance.state == "assigned":
        db.delete(current_instance)

    db.delete(assignment)
    db.commit()


def _validate_monday(d: date) -> None:
    if d.weekday() != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{d} n'est pas un lundi.",
        )
