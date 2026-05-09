import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.moment import Moment
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
    for label, start, end, order in [
        ("matin", "07:00", "12:00", 0),
        ("midi", "12:00", "14:00", 1),
        ("soir", "18:00", "21:00", 2),
    ]:
        db.add(instance=Moment(label=label, start_time=start, end_time=end, sort_order=order))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_client() -> TestClient:
    client.post("/api/v1/auth/login", json={"login": "admin", "password": "admin"})
    return client


def test_list_moments_public() -> None:
    client.cookies.clear()
    r = client.get("/api/v1/moments/")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    assert [m["label"] for m in data] == ["matin", "midi", "soir"]


def test_list_moments_sorted() -> None:
    r = client.get("/api/v1/moments/")
    assert [m["sort_order"] for m in r.json()] == [0, 1, 2]


def test_update_moment(auth_client: TestClient) -> None:
    moment_id = auth_client.get("/api/v1/moments/").json()[0]["id"]
    r = auth_client.put(f"/api/v1/moments/{moment_id}", json={"start_time": "06:30:00"})
    assert r.status_code == 200
    assert r.json()["start_time"] == "06:30:00"


def test_update_moment_requires_auth() -> None:
    client.cookies.clear()
    moment_id = client.get("/api/v1/moments/").json()[0]["id"]
    r = client.put(f"/api/v1/moments/{moment_id}", json={"start_time": "06:00:00"})
    assert r.status_code == 401
