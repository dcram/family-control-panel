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


@pytest.fixture(autouse=True)
def setup_db() -> None:  # type: ignore[return]
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add(
        instance=Parent(
            login="testparent",
            password_hash=hash_password(password="secret"),
        )
    )
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app=app, raise_server_exceptions=True)


def test_login_ok() -> None:
    r = client.post("/api/v1/auth/login", json={"login": "testparent", "password": "secret"})
    assert r.status_code == 200
    assert r.json()["login"] == "testparent"
    assert "access_token" in r.cookies


def test_login_wrong_password() -> None:
    r = client.post("/api/v1/auth/login", json={"login": "testparent", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_user() -> None:
    r = client.post("/api/v1/auth/login", json={"login": "nobody", "password": "x"})
    assert r.status_code == 401


def test_me_authenticated() -> None:
    client.post("/api/v1/auth/login", json={"login": "testparent", "password": "secret"})
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["login"] == "testparent"


def test_me_unauthenticated() -> None:
    client.cookies.clear()
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_logout() -> None:
    client.post("/api/v1/auth/login", json={"login": "testparent", "password": "secret"})
    r = client.post("/api/v1/auth/logout")
    assert r.status_code == 200
    r2 = client.get("/api/v1/auth/me")
    assert r2.status_code == 401
