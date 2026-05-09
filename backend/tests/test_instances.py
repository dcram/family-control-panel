from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.assignment import Assignment
from app.models.child import Child
from app.models.moment import Moment
from app.models.parent import Parent
from app.models.task import Task
from app.models.task_instance import TaskInstance
from app.services.instances import get_current_week_start, get_next_week_start

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


@pytest.fixture(autouse=True)
def setup_db() -> None:  # type: ignore[return]
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add(instance=Parent(login="admin", password_hash=hash_password(password="admin")))
    task = Task(label="Vaisselle", duration_minutes=15)
    child = Child(first_name="Alice", date_of_birth=date(2015, 1, 1), color="green", sort_order=0)
    moment = Moment(label="soir", start_time="18:00", end_time="21:00", sort_order=2)
    db.add_all([task, child, moment])
    db.commit()
    assignment = Assignment(
        task_id=task.id,
        child_id=child.id,
        moment_id=moment.id,
        day_of_week=0,
    )
    db.add(instance=assignment)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_client() -> TestClient:
    client.post("/api/v1/auth/login", json={"login": "admin", "password": "admin"})
    return client


def test_get_week_generates_instances(auth_client: TestClient) -> None:
    # On utilise S+1 pour éviter que les 30h ne soient déjà expirées
    week = get_next_week_start()
    r = auth_client.get(f"/api/v1/instances/week/{week}")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["task_label"] == "Vaisselle"
    assert data[0]["child_first_name"] == "Alice"
    assert data[0]["state"] == "assigned"


def test_get_week_idempotent(auth_client: TestClient) -> None:
    week = get_next_week_start()
    auth_client.get(f"/api/v1/instances/week/{week}")
    r = auth_client.get(f"/api/v1/instances/week/{week}")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_next_week(auth_client: TestClient) -> None:
    week = get_next_week_start()
    r = auth_client.get(f"/api/v1/instances/week/{week}")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_beyond_s1_rejected(auth_client: TestClient) -> None:
    week = get_next_week_start() + timedelta(weeks=1)
    r = auth_client.get(f"/api/v1/instances/week/{week}")
    assert r.status_code == 400


def test_get_not_monday_rejected(auth_client: TestClient) -> None:
    r = auth_client.get("/api/v1/instances/week/2026-05-06")
    assert r.status_code == 400


def test_30h_declared_becomes_done(auth_client: TestClient) -> None:
    week = get_current_week_start()
    past_monday = week - timedelta(weeks=2)
    db = TestingSession()
    instance = TaskInstance(
        week_start=past_monday,
        instance_date=past_monday,
        state="declared",
        declared_at=datetime.now(tz=timezone.utc) - timedelta(hours=35),
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

    r = auth_client.get(f"/api/v1/instances/week/{past_monday}")
    assert r.status_code == 200
    assert r.json()[0]["state"] == "done"


def test_30h_assigned_becomes_unknown(auth_client: TestClient) -> None:
    week = get_current_week_start()
    past_monday = week - timedelta(weeks=2)
    db = TestingSession()
    instance = TaskInstance(
        week_start=past_monday,
        instance_date=past_monday,
        state="assigned",
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

    r = auth_client.get(f"/api/v1/instances/week/{past_monday}")
    assert r.status_code == 200
    assert r.json()[0]["state"] == "unknown"
