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


def create_test_stock(client: TestClient) -> int:
    response = client.post(
        "/api/v1/stocks",
        json={
            "symbol": "RELIANCE.NS",
            "name": "Reliance Industries",
            "exchange": "NSE",
            "currency": "INR",
        },
    )

    return response.json()["id"]


def test_add_stock_to_watchlist(client: TestClient):
    stock_id = create_test_stock(client)

    response = client.post(
        "/api/v1/watchlist",
        json={"stock_id": stock_id},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["stock_id"] == stock_id
    assert data["is_active"] is True
    assert data["stock"]["symbol"] == "RELIANCE.NS"


def test_add_missing_stock_to_watchlist_returns_404(client: TestClient):
    response = client.post(
        "/api/v1/watchlist",
        json={"stock_id": 999},
    )

    assert response.status_code == 404


def test_duplicate_watchlist_item_fails(client: TestClient):
    stock_id = create_test_stock(client)

    first_response = client.post(
        "/api/v1/watchlist",
        json={"stock_id": stock_id},
    )

    second_response = client.post(
        "/api/v1/watchlist",
        json={"stock_id": stock_id},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_list_watchlist_items(client: TestClient):
    stock_id = create_test_stock(client)

    client.post(
        "/api/v1/watchlist",
        json={"stock_id": stock_id},
    )

    response = client.get("/api/v1/watchlist")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["stock_id"] == stock_id
    assert data[0]["stock"]["symbol"] == "RELIANCE.NS"


def test_delete_watchlist_item_soft_deletes(client: TestClient):
    stock_id = create_test_stock(client)

    create_response = client.post(
        "/api/v1/watchlist",
        json={"stock_id": stock_id},
    )

    watchlist_item_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/watchlist/{watchlist_item_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    list_response = client.get("/api/v1/watchlist")

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_delete_missing_watchlist_item_returns_404(client: TestClient):
    response = client.delete("/api/v1/watchlist/999")

    assert response.status_code == 404