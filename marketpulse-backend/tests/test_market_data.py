from unittest.mock import MagicMock, patch

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_quote_success():
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "currentPrice": 2900.5,
        "previousClose": 2880.0,
        "open": 2890.0,
        "dayHigh": 2920.0,
        "dayLow": 2875.0,
        "currency": "INR",
        "exchange": "NSI",
    }

    with patch("app.services.market_data_service.yf.Ticker", return_value=mock_ticker):
        response = client.get("/api/v1/market-data/RELIANCE.NS/quote")

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "RELIANCE.NS"
    assert data["current_price"] == 2900.5
    assert data["currency"] == "INR"
    assert data["exchange"] == "NSI"


def test_get_quote_returns_400_when_no_data():
    mock_ticker = MagicMock()
    mock_ticker.info = {}

    with patch("app.services.market_data_service.yf.Ticker", return_value=mock_ticker):
        response = client.get("/api/v1/market-data/INVALID/quote")

    assert response.status_code == 400


def test_get_history_success():
    mock_ticker = MagicMock()

    history_df = pd.DataFrame(
        {
            "Open": [100.0, 105.0],
            "High": [110.0, 112.0],
            "Low": [95.0, 102.0],
            "Close": [108.0, 109.0],
            "Volume": [1000000, 1200000],
        },
        index=pd.to_datetime(["2026-06-25", "2026-06-26"]),
    )

    mock_ticker.history.return_value = history_df

    with patch("app.services.market_data_service.yf.Ticker", return_value=mock_ticker):
        response = client.get(
            "/api/v1/market-data/RELIANCE.NS/history?period=1mo&interval=1d"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "RELIANCE.NS"
    assert data["period"] == "1mo"
    assert data["interval"] == "1d"
    assert len(data["prices"]) == 2
    assert data["prices"][0]["close_price"] == 108.0


def test_get_history_invalid_period_returns_400():
    response = client.get(
        "/api/v1/market-data/RELIANCE.NS/history?period=invalid&interval=1d"
    )

    assert response.status_code == 400


def test_get_history_invalid_interval_returns_400():
    response = client.get(
        "/api/v1/market-data/RELIANCE.NS/history?period=1mo&interval=invalid"
    )

    assert response.status_code == 400


def test_get_history_empty_data_returns_400():
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame()

    with patch("app.services.market_data_service.yf.Ticker", return_value=mock_ticker):
        response = client.get(
            "/api/v1/market-data/RELIANCE.NS/history?period=1mo&interval=1d"
        )

    assert response.status_code == 400