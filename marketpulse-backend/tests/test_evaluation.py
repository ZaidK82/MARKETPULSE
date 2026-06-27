from collections.abc import Generator
from unittest.mock import patch

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


def create_test_alert_rule(
    client: TestClient,
    stock_id: int,
    indicator: str = "close_price",
    operator: str = ">",
    target_value: float = 100,
) -> dict:
    response = client.post(
        "/api/v1/alert-rules",
        json={
            "stock_id": stock_id,
            "name": "AAPL Test Rule",
            "indicator": indicator,
            "operator": operator,
            "target_value": target_value,
            "direction": "bullish",
            "timeframe": "1d",
        },
    )

    return response.json()


def test_evaluate_close_price_rule_triggered(client: TestClient):
    stock_id = create_test_stock(client)

    rule = create_test_alert_rule(
        client=client,
        stock_id=stock_id,
        indicator="close_price",
        operator=">",
        target_value=100,
    )

    with patch(
        "app.services.evaluation_service.fetch_quote",
        return_value={
            "symbol": "AAPL",
            "current_price": 150.0,
        },
    ):
        response = client.post(
            f"/api/v1/evaluation/alert-rules/{rule['id']}/evaluate"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["triggered"] is True
    assert data["current_value"] == 150.0
    assert data["alert_event_id"] is not None


def test_evaluate_close_price_rule_not_triggered(client: TestClient):
    stock_id = create_test_stock(client)

    rule = create_test_alert_rule(
        client=client,
        stock_id=stock_id,
        indicator="close_price",
        operator=">",
        target_value=200,
    )

    with patch(
        "app.services.evaluation_service.fetch_quote",
        return_value={
            "symbol": "AAPL",
            "current_price": 150.0,
        },
    ):
        response = client.post(
            f"/api/v1/evaluation/alert-rules/{rule['id']}/evaluate"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["triggered"] is False
    assert data["current_value"] == 150.0
    assert data["alert_event_id"] is None


def test_evaluate_rsi_rule_triggered(client: TestClient):
    stock_id = create_test_stock(client)

    rule = create_test_alert_rule(
        client=client,
        stock_id=stock_id,
        indicator="rsi",
        operator="<",
        target_value=30,
    )

    with patch(
        "app.services.evaluation_service.calculate_rsi",
        return_value={
            "symbol": "AAPL",
            "indicator": "RSI",
            "period": "6mo",
            "interval": "1d",
            "window": 14,
            "values": [
                {"date": "2026-06-25 00:00:00", "value": 35.0},
                {"date": "2026-06-26 00:00:00", "value": 27.5},
            ],
        },
    ):
        response = client.post(
            f"/api/v1/evaluation/alert-rules/{rule['id']}/evaluate"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["triggered"] is True
    assert data["current_value"] == 27.5
    assert data["alert_event_id"] is not None


def test_evaluate_macd_histogram_rule_triggered(client: TestClient):
    stock_id = create_test_stock(client)

    rule = create_test_alert_rule(
        client=client,
        stock_id=stock_id,
        indicator="macd_histogram",
        operator=">",
        target_value=0,
    )

    with patch(
        "app.services.evaluation_service.calculate_macd",
        return_value={
            "symbol": "AAPL",
            "indicator": "MACD",
            "period": "6mo",
            "interval": "1d",
            "fast_window": 12,
            "slow_window": 26,
            "signal_window": 9,
            "values": [
                {
                    "date": "2026-06-26 00:00:00",
                    "macd": 1.2,
                    "signal": 0.8,
                    "histogram": 0.4,
                }
            ],
        },
    ):
        response = client.post(
            f"/api/v1/evaluation/alert-rules/{rule['id']}/evaluate"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["triggered"] is True
    assert data["current_value"] == 0.4
    assert data["alert_event_id"] is not None


def test_evaluate_missing_rule_returns_404(client: TestClient):
    response = client.post("/api/v1/evaluation/alert-rules/999/evaluate")

    assert response.status_code == 404


def test_evaluate_inactive_rule_returns_400(client: TestClient):
    stock_id = create_test_stock(client)
    rule = create_test_alert_rule(client=client, stock_id=stock_id)

    client.delete(f"/api/v1/alert-rules/{rule['id']}")

    response = client.post(
        f"/api/v1/evaluation/alert-rules/{rule['id']}/evaluate"
    )

    assert response.status_code == 400


def test_evaluate_rule_when_current_price_missing_returns_400(client: TestClient):
    stock_id = create_test_stock(client)
    rule = create_test_alert_rule(client=client, stock_id=stock_id)

    with patch(
        "app.services.evaluation_service.fetch_quote",
        return_value={
            "symbol": "AAPL",
            "current_price": None,
        },
    ):
        response = client.post(
            f"/api/v1/evaluation/alert-rules/{rule['id']}/evaluate"
        )

    assert response.status_code == 400