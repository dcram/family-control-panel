import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.assignment import Assignment
from app.models.child import Child
from app.models.kiosk_pin import KioskPin
from app.models.moment import Moment
from app.models.parent import Parent
from app.models.task import Task
from app.models.task_instance import TaskInstance
from app.services.instances import get_next_week_start

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

CHILD_PIN = "1234"
PARENT_PIN = "0001"
OTHER_CHILD_PIN = "5678"

INSTANCE_ID: uuid.UUID
PARENT_ID: uuid.UUID
CHILD_ID: uuid.UUID


@pytest.fixture(autouse=True)
def setup_db() -> None:  # type: ignore[return]
    global INSTANCE_ID, PARENT_ID, CHILD_ID
    Base.metadata.create_all(bind=engine)
    db = TestingSession()

    parent = Parent(login="admin", password_hash=hash_password(password="admin"))
    child = Child(first_name="Alice", date_of_birth=date(2015, 1, 1), color="green", sort_order=0)
    other_child = Child(first_name="Bob", date_of_birth=date(2016, 1, 1), color="blue", sort_order=1)
    task = Task(label="Vaisselle", duration_minutes=15)
    moment = Moment(label="soir", start_time="18:00", end_time="21:00", sort_order=2)
    db.add_all([parent, child, other_child, task, moment])
    db.flush()

    db.add_all([
        KioskPin(pin=CHILD_PIN, holder_type="child", holder_id=child.id),
        KioskPin(pin=PARENT_PIN, holder_type="parent", holder_id=parent.id),
        KioskPin(pin=OTHER_CHILD_PIN, holder_type="child", holder_id=other_child.id),
    ])

    week = get_next_week_start()
    assignment = Assignment(
        task_id=task.id, child_id=child.id, moment_id=moment.id, day_of_week=0
    )
    db.add(instance=assignment)
    db.flush()

    instance = TaskInstance(
        assignment_id=assignment.id,
        week_start=week,
        instance_date=week,
        task_label="Vaisselle",
        task_duration_minutes=15,
        child_first_name="Alice",
        child_color="green",
        moment_label="soir",
        day_of_week=0,
    )
    db.add(instance=instance)
    db.commit()

    INSTANCE_ID = instance.id
    PARENT_ID = parent.id
    CHILD_ID = child.id
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_client() -> TestClient:
    client.post("/api/v1/auth/login", json={"login": "admin", "password": "admin"})
    return client


# --- declare ---

def test_declare_ok() -> None:
    client.cookies.clear()
    r = client.post(f"/api/v1/instances/{INSTANCE_ID}/declare", json={"pin": CHILD_PIN})
    assert r.status_code == 200
    assert r.json()["state"] == "declared"


def test_declare_unknown_pin() -> None:
    r = client.post(f"/api/v1/instances/{INSTANCE_ID}/declare", json={"pin": "9999"})
    assert r.status_code == 401


def test_declare_parent_pin_rejected() -> None:
    r = client.post(f"/api/v1/instances/{INSTANCE_ID}/declare", json={"pin": PARENT_PIN})
    assert r.status_code == 403


def test_declare_wrong_child_pin() -> None:
    r = client.post(f"/api/v1/instances/{INSTANCE_ID}/declare", json={"pin": OTHER_CHILD_PIN})
    assert r.status_code == 403


def test_declare_409_if_not_assigned() -> None:
    client.post(f"/api/v1/instances/{INSTANCE_ID}/declare", json={"pin": CHILD_PIN})
    r = client.post(f"/api/v1/instances/{INSTANCE_ID}/declare", json={"pin": CHILD_PIN})
    assert r.status_code == 409


# --- validate ---

def test_validate_with_parent_pin(auth_client: TestClient) -> None:
    client.cookies.clear()
    r = client.post(
        f"/api/v1/instances/{INSTANCE_ID}/validate",
        json={"pin": PARENT_PIN, "target_state": "done"},
    )
    assert r.status_code == 200
    assert r.json()["state"] == "done"


def test_validate_with_jwt(auth_client: TestClient) -> None:
    r = auth_client.post(
        f"/api/v1/instances/{INSTANCE_ID}/validate",
        json={"target_state": "undone", "reason": "refused"},
    )
    assert r.status_code == 200
    assert r.json()["state"] == "undone"


def test_validate_no_auth() -> None:
    client.cookies.clear()
    r = client.post(
        f"/api/v1/instances/{INSTANCE_ID}/validate",
        json={"target_state": "done"},
    )
    assert r.status_code == 401


# --- reset ---

def test_reset_ok(auth_client: TestClient) -> None:
    client.post(f"/api/v1/instances/{INSTANCE_ID}/declare", json={"pin": CHILD_PIN})
    r = auth_client.post(f"/api/v1/instances/{INSTANCE_ID}/reset")
    assert r.status_code == 200
    data = r.json()
    assert data["state"] == "assigned"
    assert data["declared_at"] is None


def test_reset_requires_jwt() -> None:
    client.cookies.clear()
    r = client.post(f"/api/v1/instances/{INSTANCE_ID}/reset")
    assert r.status_code == 401
