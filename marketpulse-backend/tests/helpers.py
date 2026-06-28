from fastapi.testclient import TestClient


def create_test_stock(
    client: TestClient,
    symbol: str = "AAPL",
    name: str = "Apple Inc.",
    exchange: str = "NASDAQ",
) -> dict:
    payload = {
        "symbol": symbol,
        "name": name,
        "exchange": exchange,
    }

    response = client.post(
        "/api/v1/stocks",
        json=payload,
    )

    assert response.status_code == 201, (
        f"Failed to create stock. "
        f"Status: {response.status_code}. "
        f"Payload: {payload}. "
        f"Response: {response.text}"
    )

    return response.json()
def create_test_alert_rule(
    client: TestClient,
    stock_id: int | dict,
    name: str = "Test Alert Rule",
    indicator: str = "close_price",
    operator: str = ">",
    target_value: float = 100.0,
    timeframe: str = "1d",
    direction: str = "bullish",
) -> dict:
    if isinstance(stock_id, dict):
        stock_id = stock_id["id"]

    payload = {
        "stock_id": stock_id,
        "name": name,
        "indicator": indicator,
        "operator": operator,
        "target_value": target_value,
        "timeframe": timeframe,
        "direction": direction,
    }

    response = client.post(
        "/api/v1/alert-rules",
        json=payload,
    )

    assert response.status_code == 201, (
        f"Failed to create alert rule. "
        f"Status: {response.status_code}. "
        f"Payload: {payload}. "
        f"Response: {response.text}"
    )

    return response.json()

def post_scheduler_run_once(
    client: TestClient,
    cron_secret: str = "test-secret",
):
    return client.post(
        "/api/v1/scheduler/run-once",
        headers={"x-cron-secret": cron_secret},
    )