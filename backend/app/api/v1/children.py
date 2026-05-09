import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_parent
from app.core.database import get_db
from app.models.assignment import Assignment
from app.models.child import Child
from app.models.parent import Parent
from app.schemas.child import CHILD_COLORS, ChildCreate, ChildOut, ChildUpdate

router = APIRouter(prefix="/children", tags=["children"])


def _get_child_or_404(child_id: uuid.UUID, db: Session) -> Child:
    child = db.get(entity=Child, ident=child_id)
    if not child or child.archived_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enfant introuvable")
    return child


@router.get("/")
def list_children(
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> list[ChildOut]:
    rows = db.scalars(
        select(Child)
        .where(Child.archived_at.is_(None))
        .order_by(Child.sort_order)
    ).all()
    return [ChildOut.model_validate(obj=r) for r in rows]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_child(
    body: ChildCreate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> ChildOut:
    count = db.scalar(
        select(func.count()).select_from(Child).where(Child.archived_at.is_(None))
    ) or 0
    color = CHILD_COLORS[count % len(CHILD_COLORS)]
    sort_order = db.scalar(
        select(func.coalesce(func.max(Child.sort_order) + 1, 0))
    ) or 0
    child = Child(
        first_name=body.first_name,
        date_of_birth=body.date_of_birth,
        color=color,
        sort_order=sort_order,
    )
    db.add(instance=child)
    db.commit()
    db.refresh(instance=child)
    return ChildOut.model_validate(obj=child)


@router.put("/{child_id}")
def update_child(
    child_id: uuid.UUID,
    body: ChildUpdate,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> ChildOut:
    child = _get_child_or_404(child_id=child_id, db=db)
    if body.first_name is not None:
        child.first_name = body.first_name
    if body.date_of_birth is not None:
        child.date_of_birth = body.date_of_birth
    db.commit()
    db.refresh(instance=child)
    return ChildOut.model_validate(obj=child)


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Parent = Depends(get_current_parent),
) -> None:
    child = _get_child_or_404(child_id=child_id, db=db)
    db.execute(delete(Assignment).where(Assignment.child_id == child_id))
    child.archived_at = datetime.now(tz=timezone.utc)
    db.commit()
