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
    target_value: float = 100,
) -> dict:
    response = client.post(
        "/api/v1/alert-rules",
        json={
            "stock_id": stock_id,
            "name": "AAPL Close Price Above Target",
            "indicator": "close_price",
            "operator": ">",
            "target_value": target_value,
            "direction": "bullish",
            "timeframe": "1d",
        },
    )

    return response.json()


def test_scheduler_status(client: TestClient):
    response = client.get("/api/v1/scheduler/status")

    assert response.status_code == 200

    data = response.json()

    assert "scheduler_enabled" in data
    assert "interval_minutes" in data
    assert data["mode"] in {"manual-run-once", "background-enabled"}


def test_scheduler_run_once_with_no_rules(client: TestClient):
    response = client.post("/api/v1/scheduler/run-once")

    assert response.status_code == 200

    data = response.json()

    assert data["evaluated_rules"] == 0
    assert data["triggered_rules"] == 0
    assert data["notifications_attempted"] == 0
    assert data["notifications_sent"] == 0
    assert data["errors"] == []


def test_scheduler_run_once_triggered_and_notification_sent(client: TestClient):
    stock_id = create_test_stock(client)
    create_test_alert_rule(client, stock_id, target_value=100)

    with patch(
        "app.services.evaluation_service.fetch_quote",
        return_value={
            "symbol": "AAPL",
            "current_price": 150.0,
        },
    ), patch(
        "app.services.scheduler_service.send_discord_notification",
        return_value={
            "alert_event_id": 1,
            "channel": "discord",
            "status": "sent",
            "response_message": "Discord notification sent successfully.",
            "notification_log_id": 1,
        },
    ):
        response = client.post("/api/v1/scheduler/run-once")

    assert response.status_code == 200

    data = response.json()

    assert data["evaluated_rules"] == 1
    assert data["triggered_rules"] == 1
    assert data["notifications_attempted"] == 1
    assert data["notifications_sent"] == 1
    assert data["errors"] == []


def test_scheduler_run_once_not_triggered(client: TestClient):
    stock_id = create_test_stock(client)
    create_test_alert_rule(client, stock_id, target_value=200)

    with patch(
        "app.services.evaluation_service.fetch_quote",
        return_value={
            "symbol": "AAPL",
            "current_price": 150.0,
        },
    ):
        response = client.post("/api/v1/scheduler/run-once")

    assert response.status_code == 200

    data = response.json()

    assert data["evaluated_rules"] == 1
    assert data["triggered_rules"] == 0
    assert data["notifications_attempted"] == 0
    assert data["notifications_sent"] == 0
    assert data["errors"] == []


def test_scheduler_run_once_notification_failure_is_recorded(client: TestClient):
    stock_id = create_test_stock(client)
    create_test_alert_rule(client, stock_id, target_value=100)

    with patch(
        "app.services.evaluation_service.fetch_quote",
        return_value={
            "symbol": "AAPL",
            "current_price": 150.0,
        },
    ), patch(
        "app.services.scheduler_service.send_discord_notification",
        side_effect=Exception("Discord failed"),
    ):
        response = client.post("/api/v1/scheduler/run-once")

    assert response.status_code == 200

    data = response.json()

    assert data["evaluated_rules"] == 1
    assert data["triggered_rules"] == 1
    assert data["notifications_attempted"] == 1
    assert data["notifications_sent"] == 0
    assert len(data["errors"]) == 1