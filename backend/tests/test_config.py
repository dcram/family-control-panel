import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.kiosk_config import KioskConfig
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
    db.add(instance=KioskConfig(id=1))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_client() -> TestClient:
    client.post("/api/v1/auth/login", json={"login": "admin", "password": "admin"})
    return client


def test_get_config_public() -> None:
    client.cookies.clear()
    r = client.get("/api/v1/config/")
    assert r.status_code == 200
    assert r.json()["weather_city"] == "Paris"


def test_update_weather(auth_client: TestClient) -> None:
    r = auth_client.put("/api/v1/config/weather", json={"weather_city": "Lyon"})
    assert r.status_code == 200
    assert r.json()["weather_city"] == "Lyon"
    assert client.get("/api/v1/config/").json()["weather_city"] == "Lyon"


def test_update_quote(auth_client: TestClient) -> None:
    r = auth_client.put(
        "/api/v1/config/quote",
        json={"quote_text": "Connais-toi toi-même", "quote_author": "Socrate"},
    )
    assert r.status_code == 200
    assert r.json()["quote_text"] == "Connais-toi toi-même"


def test_update_requires_auth() -> None:
    client.cookies.clear()
    assert client.put("/api/v1/config/weather", json={"weather_city": "Nice"}).status_code == 401
