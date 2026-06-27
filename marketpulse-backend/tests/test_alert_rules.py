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
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
        },
    )

    return response.json()["id"]


def create_test_alert_rule(client: TestClient, stock_id: int) -> dict:
    response = client.post(
        "/api/v1/alert-rules",
        json={
            "stock_id": stock_id,
            "name": "AAPL RSI Oversold",
            "indicator": "rsi",
            "operator": "<",
            "target_value": 30,
            "direction": "bullish",
            "timeframe": "1d",
        },
    )

    return response.json()


def test_create_alert_rule(client: TestClient):
    stock_id = create_test_stock(client)

    response = client.post(
        "/api/v1/alert-rules",
        json={
            "stock_id": stock_id,
            "name": "AAPL RSI Oversold",
            "indicator": "rsi",
            "operator": "<",
            "target_value": 30,
            "direction": "bullish",
            "timeframe": "1d",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["stock_id"] == stock_id
    assert data["name"] == "AAPL RSI Oversold"
    assert data["indicator"] == "rsi"
    assert data["operator"] == "<"
    assert data["target_value"] == 30
    assert data["direction"] == "bullish"
    assert data["timeframe"] == "1d"
    assert data["is_active"] is True


def test_create_alert_rule_for_missing_stock_returns_404(client: TestClient):
    response = client.post(
        "/api/v1/alert-rules",
        json={
            "stock_id": 999,
            "name": "Missing Stock Rule",
            "indicator": "rsi",
            "operator": "<",
            "target_value": 30,
            "direction": "bullish",
            "timeframe": "1d",
        },
    )

    assert response.status_code == 404


def test_create_alert_rule_with_invalid_indicator_returns_422(client: TestClient):
    stock_id = create_test_stock(client)

    response = client.post(
        "/api/v1/alert-rules",
        json={
            "stock_id": stock_id,
            "name": "Invalid Indicator Rule",
            "indicator": "invalid_indicator",
            "operator": "<",
            "target_value": 30,
            "direction": "bullish",
            "timeframe": "1d",
        },
    )

    assert response.status_code == 422


def test_create_alert_rule_with_invalid_operator_returns_422(client: TestClient):
    stock_id = create_test_stock(client)

    response = client.post(
        "/api/v1/alert-rules",
        json={
            "stock_id": stock_id,
            "name": "Invalid Operator Rule",
            "indicator": "rsi",
            "operator": "crosses",
            "target_value": 30,
            "direction": "bullish",
            "timeframe": "1d",
        },
    )

    assert response.status_code == 422


def test_list_alert_rules(client: TestClient):
    stock_id = create_test_stock(client)
    create_test_alert_rule(client, stock_id)

    response = client.get("/api/v1/alert-rules")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["indicator"] == "rsi"


def test_get_alert_rule_by_id(client: TestClient):
    stock_id = create_test_stock(client)
    created_rule = create_test_alert_rule(client, stock_id)

    response = client.get(f"/api/v1/alert-rules/{created_rule['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created_rule["id"]


def test_get_missing_alert_rule_returns_404(client: TestClient):
    response = client.get("/api/v1/alert-rules/999")

    assert response.status_code == 404


def test_update_alert_rule(client: TestClient):
    stock_id = create_test_stock(client)
    created_rule = create_test_alert_rule(client, stock_id)

    response = client.patch(
        f"/api/v1/alert-rules/{created_rule['id']}",
        json={
            "target_value": 35,
            "direction": "neutral",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["target_value"] == 35
    assert data["direction"] == "neutral"


def test_update_missing_alert_rule_returns_404(client: TestClient):
    response = client.patch(
        "/api/v1/alert-rules/999",
        json={
            "target_value": 35,
        },
    )

    assert response.status_code == 404


def test_delete_alert_rule_soft_deletes(client: TestClient):
    stock_id = create_test_stock(client)
    created_rule = create_test_alert_rule(client, stock_id)

    delete_response = client.delete(f"/api/v1/alert-rules/{created_rule['id']}")

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False

    list_response = client.get("/api/v1/alert-rules")

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_list_alert_rules_with_active_only_false(client: TestClient):
    stock_id = create_test_stock(client)
    created_rule = create_test_alert_rule(client, stock_id)

    client.delete(f"/api/v1/alert-rules/{created_rule['id']}")

    response = client.get("/api/v1/alert-rules?active_only=false")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["is_active"] is False


def test_delete_missing_alert_rule_returns_404(client: TestClient):
    response = client.delete("/api/v1/alert-rules/999")

    assert response.status_code == 404