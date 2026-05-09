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
from app.models.kiosk_config import KioskConfig
from app.models.moment import Moment
from app.models.parent import Parent
from app.models.task import Task
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
    db.add(instance=KioskConfig(id=1, quote_text="Carpe diem", quote_author="Horace"))
    task = Task(label="Vaisselle", duration_minutes=15)
    child = Child(first_name="Alice", date_of_birth=date(2015, 1, 1), color="green", sort_order=0)
    moment = Moment(label="soir", start_time="18:00", end_time="21:00", sort_order=2)
    db.add_all([task, child, moment])
    db.flush()
    db.add(instance=Assignment(
        task_id=task.id, child_id=child.id, moment_id=moment.id, day_of_week=0
    ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_kiosk_info_public() -> None:
    r = client.get("/api/v1/kiosk/info")
    assert r.status_code == 200
    data = r.json()
    assert "date" in data
    assert data["quote_text"] == "Carpe diem"
    assert data["quote_author"] == "Horace"
    assert isinstance(data["saint"], str) or data["saint"] is None
    # weather est None si pas de clé API configurée en test
    assert data["weather"] is None or isinstance(data["weather"], str)


def test_kiosk_week_public() -> None:
    week = get_next_week_start()
    r = client.get(f"/api/v1/kiosk/week/{week}")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["task_label"] == "Vaisselle"


def test_kiosk_week_no_auth_required() -> None:
    client.cookies.clear()
    week = get_next_week_start()
    r = client.get(f"/api/v1/kiosk/week/{week}")
    assert r.status_code == 200


def test_kiosk_week_not_monday() -> None:
    r = client.get("/api/v1/kiosk/week/2026-05-06")
    assert r.status_code == 400


def test_kiosk_week_beyond_s1() -> None:
    from datetime import timedelta
    week = get_next_week_start() + timedelta(weeks=1)
    r = client.get(f"/api/v1/kiosk/week/{week}")
    assert r.status_code == 400
