from collections.abc import Generator
from unittest.mock import MagicMock, patch

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


def create_triggered_alert_event(client: TestClient) -> int:
    stock_id = create_test_stock(client)

    rule_response = client.post(
        "/api/v1/alert-rules",
        json={
            "stock_id": stock_id,
            "name": "AAPL Close Price Above 100",
            "indicator": "close_price",
            "operator": ">",
            "target_value": 100,
            "direction": "bullish",
            "timeframe": "1d",
        },
    )

    rule_id = rule_response.json()["id"]

    with patch(
        "app.services.evaluation_service.fetch_quote",
        return_value={
            "symbol": "AAPL",
            "current_price": 150.0,
        },
    ):
        evaluation_response = client.post(
            f"/api/v1/evaluation/alert-rules/{rule_id}/evaluate"
        )

    return evaluation_response.json()["alert_event_id"]


def test_send_discord_notification_success(client: TestClient):
    alert_event_id = create_triggered_alert_event(client)

    mock_response = MagicMock()
    mock_response.status_code = 204

    with patch(
        "app.services.notification_service.settings.DISCORD_WEBHOOK_URL",
        "https://discord.com/api/webhooks/test",
    ), patch(
        "app.services.notification_service.requests.post",
        return_value=mock_response,
    ) as mock_post:
        response = client.post(
            f"/api/v1/notifications/alert-events/{alert_event_id}/discord"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["alert_event_id"] == alert_event_id
    assert data["channel"] == "discord"
    assert data["status"] == "sent"
    assert data["notification_log_id"] is not None

    mock_post.assert_called_once()


def test_send_discord_notification_missing_event_returns_404(client: TestClient):
    response = client.post(
        "/api/v1/notifications/alert-events/999/discord"
    )

    assert response.status_code == 404


def test_send_discord_notification_without_webhook_returns_400(client: TestClient):
    alert_event_id = create_triggered_alert_event(client)

    with patch(
        "app.services.notification_service.settings.DISCORD_WEBHOOK_URL",
        None,
    ):
        response = client.post(
            f"/api/v1/notifications/alert-events/{alert_event_id}/discord"
        )

    assert response.status_code == 400


def test_send_discord_notification_discord_failure_returns_400(client: TestClient):
    alert_event_id = create_triggered_alert_event(client)

    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch(
        "app.services.notification_service.settings.DISCORD_WEBHOOK_URL",
        "https://discord.com/api/webhooks/test",
    ), patch(
        "app.services.notification_service.requests.post",
        return_value=mock_response,
    ):
        response = client.post(
            f"/api/v1/notifications/alert-events/{alert_event_id}/discord"
        )

    assert response.status_code == 400


def test_list_notification_logs(client: TestClient):
    alert_event_id = create_triggered_alert_event(client)

    mock_response = MagicMock()
    mock_response.status_code = 204

    with patch(
        "app.services.notification_service.settings.DISCORD_WEBHOOK_URL",
        "https://discord.com/api/webhooks/test",
    ), patch(
        "app.services.notification_service.requests.post",
        return_value=mock_response,
    ):
        client.post(
            f"/api/v1/notifications/alert-events/{alert_event_id}/discord"
        )

    response = client.get("/api/v1/notifications/logs")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["alert_event_id"] == alert_event_id
    assert data[0]["channel"] == "discord"
    assert data[0]["status"] == "sent"


def test_list_alert_events(client: TestClient):
    alert_event_id = create_triggered_alert_event(client)

    response = client.get("/api/v1/notifications/alert-events")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == alert_event_id