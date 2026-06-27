from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_stock(client: TestClient):
    response = client.post(
        "/api/v1/stocks",
        json={
            "symbol": "RELIANCE.NS",
            "name": "Reliance Industries",
            "exchange": "NSE",
            "currency": "INR",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["symbol"] == "RELIANCE.NS"
    assert data["name"] == "Reliance Industries"
    assert data["exchange"] == "NSE"
    assert data["currency"] == "INR"


def test_create_duplicate_stock_fails(client: TestClient):
    payload = {
        "symbol": "TCS.NS",
        "name": "Tata Consultancy Services",
        "exchange": "NSE",
        "currency": "INR",
    }

    first_response = client.post("/api/v1/stocks", json=payload)
    second_response = client.post("/api/v1/stocks", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_list_stocks(client: TestClient):
    client.post(
        "/api/v1/stocks",
        json={
            "symbol": "INFY.NS",
            "name": "Infosys",
            "exchange": "NSE",
            "currency": "INR",
        },
    )

    response = client.get("/api/v1/stocks")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["symbol"] == "INFY.NS"


def test_get_stock_by_id(client: TestClient):
    create_response = client.post(
        "/api/v1/stocks",
        json={
            "symbol": "HDFCBANK.NS",
            "name": "HDFC Bank",
            "exchange": "NSE",
            "currency": "INR",
        },
    )

    stock_id = create_response.json()["id"]

    response = client.get(f"/api/v1/stocks/{stock_id}")

    assert response.status_code == 200
    assert response.json()["symbol"] == "HDFCBANK.NS"


def test_get_missing_stock_returns_404(client: TestClient):
    response = client.get("/api/v1/stocks/999")

    assert response.status_code == 404