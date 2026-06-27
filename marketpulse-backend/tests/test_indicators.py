from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


MOCK_HISTORY = {
    "symbol": "RELIANCE.NS",
    "period": "6mo",
    "interval": "1d",
    "prices": [
        {
            "date": "2026-06-01 00:00:00",
            "open_price": 100.0,
            "high_price": 105.0,
            "low_price": 95.0,
            "close_price": 100.0,
            "volume": 1000,
        },
        {
            "date": "2026-06-02 00:00:00",
            "open_price": 102.0,
            "high_price": 106.0,
            "low_price": 98.0,
            "close_price": 102.0,
            "volume": 1000,
        },
        {
            "date": "2026-06-03 00:00:00",
            "open_price": 104.0,
            "high_price": 108.0,
            "low_price": 100.0,
            "close_price": 104.0,
            "volume": 1000,
        },
        {
            "date": "2026-06-04 00:00:00",
            "open_price": 103.0,
            "high_price": 109.0,
            "low_price": 101.0,
            "close_price": 103.0,
            "volume": 1000,
        },
        {
            "date": "2026-06-05 00:00:00",
            "open_price": 106.0,
            "high_price": 110.0,
            "low_price": 102.0,
            "close_price": 106.0,
            "volume": 1000,
        },
    ],
}


def test_get_sma_success():
    with patch(
        "app.services.indicator_service.fetch_history",
        return_value=MOCK_HISTORY,
    ):
        response = client.get(
            "/api/v1/indicators/RELIANCE.NS/sma?window=3&period=6mo&interval=1d"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "RELIANCE.NS"
    assert data["indicator"] == "SMA"
    assert data["window"] == 3
    assert len(data["values"]) == 5
    assert data["values"][0]["value"] is None
    assert data["values"][2]["value"] == 102.0


def test_get_ema_success():
    with patch(
        "app.services.indicator_service.fetch_history",
        return_value=MOCK_HISTORY,
    ):
        response = client.get(
            "/api/v1/indicators/RELIANCE.NS/ema?window=3&period=6mo&interval=1d"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "RELIANCE.NS"
    assert data["indicator"] == "EMA"
    assert data["window"] == 3
    assert len(data["values"]) == 5
    assert data["values"][0]["value"] == 100.0


def test_get_rsi_success():
    with patch(
        "app.services.indicator_service.fetch_history",
        return_value=MOCK_HISTORY,
    ):
        response = client.get(
            "/api/v1/indicators/RELIANCE.NS/rsi?window=3&period=6mo&interval=1d"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "RELIANCE.NS"
    assert data["indicator"] == "RSI"
    assert data["window"] == 3
    assert len(data["values"]) == 5


def test_get_macd_success():
    with patch(
        "app.services.indicator_service.fetch_history",
        return_value=MOCK_HISTORY,
    ):
        response = client.get(
            "/api/v1/indicators/RELIANCE.NS/macd"
            "?fast_window=2&slow_window=4&signal_window=2&period=6mo&interval=1d"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "RELIANCE.NS"
    assert data["indicator"] == "MACD"
    assert data["fast_window"] == 2
    assert data["slow_window"] == 4
    assert data["signal_window"] == 2
    assert len(data["values"]) == 5
    assert "macd" in data["values"][0]
    assert "signal" in data["values"][0]
    assert "histogram" in data["values"][0]


def test_macd_invalid_window_returns_400():
    response = client.get(
        "/api/v1/indicators/RELIANCE.NS/macd"
        "?fast_window=10&slow_window=5&signal_window=2"
    )

    assert response.status_code == 400


def test_indicator_invalid_query_window_returns_422():
    response = client.get(
        "/api/v1/indicators/RELIANCE.NS/sma?window=0"
    )

    assert response.status_code == 422