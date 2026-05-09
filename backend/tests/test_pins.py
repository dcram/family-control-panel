from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.child import Child
from app.models.parent import Parent

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

CHILD_ID: str


@pytest.fixture(autouse=True)
def setup_db() -> None:  # type: ignore[return]
    global CHILD_ID
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add(instance=Parent(login="admin", password_hash=hash_password(password="admin")))
    child = Child(first_name="Alice", date_of_birth=date(2015, 1, 1), color="green", sort_order=0)
    db.add(instance=child)
    db.commit()
    CHILD_ID = str(child.id)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_client() -> TestClient:
    client.post("/api/v1/auth/login", json={"login": "admin", "password": "admin"})
    return client


# --- PIN enfant ---

def test_child_pin_initially_null(auth_client: TestClient) -> None:
    r = auth_client.get(f"/api/v1/children/{CHILD_ID}/pin")
    assert r.status_code == 200
    assert r.json()["pin"] is None


def test_set_child_pin(auth_client: TestClient) -> None:
    r = auth_client.post(f"/api/v1/children/{CHILD_ID}/pin", json={"pin": "1234"})
    assert r.status_code == 200
    assert r.json()["pin"] == "1234"


def test_get_child_pin_after_set(auth_client: TestClient) -> None:
    auth_client.post(f"/api/v1/children/{CHILD_ID}/pin", json={"pin": "5678"})
    r = auth_client.get(f"/api/v1/children/{CHILD_ID}/pin")
    assert r.json()["pin"] == "5678"


def test_update_child_pin(auth_client: TestClient) -> None:
    auth_client.post(f"/api/v1/children/{CHILD_ID}/pin", json={"pin": "1111"})
    auth_client.post(f"/api/v1/children/{CHILD_ID}/pin", json={"pin": "2222"})
    r = auth_client.get(f"/api/v1/children/{CHILD_ID}/pin")
    assert r.json()["pin"] == "2222"


def test_pin_conflict(auth_client: TestClient) -> None:
    db = TestingSession()
    child2 = Child(first_name="Bob", date_of_birth=date(2016, 1, 1), color="blue", sort_order=1)
    db.add(instance=child2)
    db.commit()
    child2_id = str(child2.id)
    db.close()
    auth_client.post(f"/api/v1/children/{CHILD_ID}/pin", json={"pin": "9999"})
    r = auth_client.post(f"/api/v1/children/{child2_id}/pin", json={"pin": "9999"})
    assert r.status_code == 409


def test_pin_invalid_format(auth_client: TestClient) -> None:
    r = auth_client.post(f"/api/v1/children/{CHILD_ID}/pin", json={"pin": "abc"})
    assert r.status_code == 422


# --- PIN parent ---

def test_parent_pin_initially_null(auth_client: TestClient) -> None:
    r = auth_client.get("/api/v1/auth/pin")
    assert r.status_code == 200
    assert r.json()["pin"] is None


def test_set_parent_pin(auth_client: TestClient) -> None:
    r = auth_client.post("/api/v1/auth/pin", json={"pin": "0001"})
    assert r.status_code == 200
    assert r.json()["pin"] == "0001"


def test_parent_pin_usable_for_verify(auth_client: TestClient) -> None:
    auth_client.post("/api/v1/auth/pin", json={"pin": "0001"})
    client.cookies.clear()
    r = client.post("/api/v1/auth/verify-pin", json={"pin": "0001"})
    assert r.status_code == 200
    assert r.json()["holder_type"] == "parent"
