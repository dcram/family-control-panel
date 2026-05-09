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


def test_list_tasks_empty(auth_client: TestClient) -> None:
    r = auth_client.get("/api/v1/tasks/")
    assert r.status_code == 200
    assert r.json() == []


def test_create_task(auth_client: TestClient) -> None:
    r = auth_client.post(
        "/api/v1/tasks/",
        json={"label": "Faire la vaisselle", "emoji": "🍽️", "min_age": 8, "duration_minutes": 15},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["label"] == "Faire la vaisselle"
    assert data["emoji"] == "🍽️"
    assert data["min_age"] == 8
    assert data["duration_minutes"] == 15


def test_create_task_without_emoji(auth_client: TestClient) -> None:
    r = auth_client.post(
        "/api/v1/tasks/",
        json={"label": "Ranger sa chambre", "duration_minutes": 20},
    )
    assert r.status_code == 201
    assert r.json()["emoji"] is None


def test_update_task(auth_client: TestClient) -> None:
    task_id = auth_client.post(
        "/api/v1/tasks/",
        json={"label": "Passer l'aspirateur", "duration_minutes": 30},
    ).json()["id"]
    r = auth_client.put(f"/api/v1/tasks/{task_id}", json={"duration_minutes": 45})
    assert r.status_code == 200
    assert r.json()["duration_minutes"] == 45


def test_delete_task_soft(auth_client: TestClient) -> None:
    task_id = auth_client.post(
        "/api/v1/tasks/",
        json={"label": "Mettre la table", "duration_minutes": 10},
    ).json()["id"]
    r = auth_client.delete(f"/api/v1/tasks/{task_id}")
    assert r.status_code == 204
    tasks = auth_client.get("/api/v1/tasks/").json()
    assert all(t["id"] != task_id for t in tasks)


def test_require_auth() -> None:
    client.cookies.clear()
    assert client.get("/api/v1/tasks/").status_code == 401
