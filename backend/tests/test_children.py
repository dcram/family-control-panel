import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
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


@pytest.fixture(autouse=True)
def setup_db() -> None:  # type: ignore[return]
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add(instance=Parent(login="admin", password_hash=hash_password(password="admin")))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_client() -> TestClient:
    client.post("/api/v1/auth/login", json={"login": "admin", "password": "admin"})
    return client


def test_list_children_empty(auth_client: TestClient) -> None:
    r = auth_client.get("/api/v1/children/")
    assert r.status_code == 200
    assert r.json() == []


def test_create_child(auth_client: TestClient) -> None:
    r = auth_client.post(
        "/api/v1/children/",
        json={"first_name": "Alice", "date_of_birth": "2015-03-10"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["first_name"] == "Alice"
    assert data["color"] == "green"
    assert data["sort_order"] == 0


def test_color_cycle(auth_client: TestClient) -> None:
    names = ["A", "B", "C", "D", "E", "F", "G"]
    colors = ["green", "blue", "amber", "coral", "purple", "gray", "green"]
    for name, expected_color in zip(names, colors):
        r = auth_client.post(
            "/api/v1/children/",
            json={"first_name": name, "date_of_birth": "2015-01-01"},
        )
        assert r.json()["color"] == expected_color


def test_update_child(auth_client: TestClient) -> None:
    child_id = auth_client.post(
        "/api/v1/children/",
        json={"first_name": "Bob", "date_of_birth": "2016-06-01"},
    ).json()["id"]
    r = auth_client.put(f"/api/v1/children/{child_id}", json={"first_name": "Robert"})
    assert r.status_code == 200
    assert r.json()["first_name"] == "Robert"


def test_delete_child_soft(auth_client: TestClient) -> None:
    child_id = auth_client.post(
        "/api/v1/children/",
        json={"first_name": "Eve", "date_of_birth": "2017-09-15"},
    ).json()["id"]
    r = auth_client.delete(f"/api/v1/children/{child_id}")
    assert r.status_code == 204
    children = auth_client.get("/api/v1/children/").json()
    assert all(c["id"] != child_id for c in children)


def test_require_auth() -> None:
    client.cookies.clear()
    r = client.get("/api/v1/children/")
    assert r.status_code == 401
