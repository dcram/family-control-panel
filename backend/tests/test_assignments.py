import uuid
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.child import Child
from app.models.moment import Moment
from app.models.parent import Parent
from app.models.task import Task
from app.models.task_instance import TaskInstance
from app.services.instances import get_current_week_start

TEST_DB_URL = "postgresql://fcp:fcp@localhost:5432/fcp_test"

engine = create_engine(url=TEST_DB_URL)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Session:  # type: ignore[override]
    db = TestingSession()
    try:
        yield db  # type: ignore[misc]
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app=app)

TASK_ID: uuid.UUID
CHILD_ID: uuid.UUID
MOMENT_ID: uuid.UUID


@pytest.fixture(autouse=True)
def setup_db() -> None:  # type: ignore[return]
    global TASK_ID, CHILD_ID, MOMENT_ID
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add(instance=Parent(login="admin", password_hash=hash_password(password="admin")))
    task = Task(label="Vaisselle", duration_minutes=15)
    child = Child(first_name="Alice", date_of_birth=date(2015, 1, 1), color="green", sort_order=0)
    moment = Moment(label="soir", start_time="18:00", end_time="21:00", sort_order=2)
    db.add_all([task, child, moment])
    db.commit()
    TASK_ID = task.id
    CHILD_ID = child.id
    MOMENT_ID = moment.id
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_client() -> TestClient:
    client.post("/api/v1/auth/login", json={"login": "admin", "password": "admin"})
    return client


def _create_assignment(auth_client: TestClient, day: int = 0) -> dict[str, object]:
    r = auth_client.post(
        "/api/v1/assignments/",
        json={
            "task_id": str(TASK_ID),
            "child_id": str(CHILD_ID),
            "moment_id": str(MOMENT_ID),
            "day_of_week": day,
        },
    )
    assert r.status_code == 201
    return dict(r.json())


def test_list_assignments_empty(auth_client: TestClient) -> None:
    r = auth_client.get("/api/v1/assignments/")
    assert r.status_code == 200
    assert r.json() == []


def test_create_assignment(auth_client: TestClient) -> None:
    data = _create_assignment(auth_client=auth_client)
    assert data["task_id"] == str(TASK_ID)
    assert data["day_of_week"] == 0


def test_create_assignment_materializes_instance(auth_client: TestClient) -> None:
    week_start = get_current_week_start()
    db = TestingSession()
    db.add(
        instance=TaskInstance(
            week_start=week_start,
            instance_date=week_start,
            task_label="dummy",
            task_duration_minutes=10,
            child_first_name="X",
            child_color="green",
            moment_label="soir",
            day_of_week=0,
        )
    )
    db.commit()
    db.close()

    _create_assignment(auth_client=auth_client)

    db = TestingSession()
    from sqlalchemy import select
    from app.models.assignment import Assignment
    assignment = db.scalar(select(Assignment))
    assert assignment is not None
    instance = db.scalar(
        select(TaskInstance).where(
            TaskInstance.assignment_id == assignment.id,
            TaskInstance.week_start == week_start,
        )
    )
    db.close()
    assert instance is not None
    assert instance.task_label == "Vaisselle"


def test_update_assignment(auth_client: TestClient) -> None:
    data = _create_assignment(auth_client=auth_client)
    r = auth_client.put(
        f"/api/v1/assignments/{data['id']}",
        json={"day_of_week": 2},
    )
    assert r.status_code == 200
    assert r.json()["day_of_week"] == 2


def test_delete_assignment(auth_client: TestClient) -> None:
    data = _create_assignment(auth_client=auth_client)
    r = auth_client.delete(f"/api/v1/assignments/{data['id']}")
    assert r.status_code == 204
    assert auth_client.get("/api/v1/assignments/").json() == []


def test_delete_assignment_409_if_instance_not_assigned(auth_client: TestClient) -> None:
    data = _create_assignment(auth_client=auth_client)
    week_start = get_current_week_start()
    db = TestingSession()
    from sqlalchemy import select
    from app.models.assignment import Assignment
    assignment = db.scalar(select(Assignment))
    assert assignment is not None
    instance = TaskInstance(
        assignment_id=assignment.id,
        week_start=week_start,
        instance_date=week_start,
        state="declared",
        task_label="Vaisselle",
        task_duration_minutes=15,
        child_first_name="Alice",
        child_color="green",
        moment_label="soir",
        day_of_week=0,
    )
    db.add(instance=instance)
    db.commit()
    db.close()

    r = auth_client.delete(f"/api/v1/assignments/{data['id']}")
    assert r.status_code == 409


def test_clone_week(auth_client: TestClient) -> None:
    _create_assignment(auth_client=auth_client)
    source = get_current_week_start()
    target = source + timedelta(weeks=2)

    db = TestingSession()
    from sqlalchemy import select
    from app.models.assignment import Assignment
    assignment = db.scalar(select(Assignment))
    assert assignment is not None
    db.add(
        instance=TaskInstance(
            assignment_id=assignment.id,
            week_start=source,
            instance_date=source,
            task_label="Vaisselle",
            task_duration_minutes=15,
            child_first_name="Alice",
            child_color="green",
            moment_label="soir",
            day_of_week=0,
        )
    )
    db.commit()
    db.close()

    r = auth_client.post(
        "/api/v1/assignments/clone",
        json={
            "source_week": str(source),
            "target_week": str(target),
            "overwrite": False,
        },
    )
    assert r.status_code == 200
    result = r.json()
    assert result["created"] == 1
    assert result["skipped"] == 0


def test_clone_invalid_day(auth_client: TestClient) -> None:
    r = auth_client.post(
        "/api/v1/assignments/clone",
        json={
            "source_week": "2026-05-06",
            "target_week": "2026-05-11",
            "overwrite": False,
        },
    )
    assert r.status_code == 400
