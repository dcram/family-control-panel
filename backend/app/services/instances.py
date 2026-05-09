from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.child import Child
from app.models.moment import Moment
from app.models.task import Task
from app.models.task_instance import TaskInstance

TZ_PARIS = ZoneInfo("Europe/Paris")


def get_current_week_start() -> date:
    today = datetime.now(tz=TZ_PARIS).date()
    return today - timedelta(days=today.weekday())


def get_next_week_start() -> date:
    return get_current_week_start() + timedelta(weeks=1)


def is_week_materialized(db: Session, week_start: date) -> bool:
    count = db.scalar(
        select(func.count())
        .select_from(TaskInstance)
        .where(TaskInstance.week_start == week_start)
    )
    return (count or 0) > 0


def get_instance_for_week(
    db: Session, assignment_id: object, week_start: date
) -> TaskInstance | None:
    return db.scalar(
        select(TaskInstance).where(
            TaskInstance.assignment_id == assignment_id,
            TaskInstance.week_start == week_start,
        )
    )


def build_instance(
    db: Session, assignment: Assignment, week_start: date
) -> TaskInstance:
    task = db.get(entity=Task, ident=assignment.task_id)
    child = db.get(entity=Child, ident=assignment.child_id)
    moment = db.get(entity=Moment, ident=assignment.moment_id)
    assert task and child and moment
    instance_date = week_start + timedelta(days=assignment.day_of_week)
    return TaskInstance(
        assignment_id=assignment.id,
        week_start=week_start,
        instance_date=instance_date,
        task_label=task.label,
        task_emoji=task.emoji,
        task_duration_minutes=task.duration_minutes,
        child_first_name=child.first_name,
        child_color=child.color,
        moment_label=moment.label,
        day_of_week=assignment.day_of_week,
    )


def refresh_instance_snapshot(
    db: Session, instance: TaskInstance, assignment: Assignment
) -> None:
    task = db.get(entity=Task, ident=assignment.task_id)
    child = db.get(entity=Child, ident=assignment.child_id)
    moment = db.get(entity=Moment, ident=assignment.moment_id)
    assert task and child and moment
    instance.task_label = task.label
    instance.task_emoji = task.emoji
    instance.task_duration_minutes = task.duration_minutes
    instance.child_first_name = child.first_name
    instance.child_color = child.color
    instance.moment_label = moment.label
    instance.day_of_week = assignment.day_of_week
    instance.instance_date = instance.week_start + timedelta(days=assignment.day_of_week)
