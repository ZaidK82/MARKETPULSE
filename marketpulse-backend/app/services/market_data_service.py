import math
from typing import Any

import pandas as pd
import yfinance as yf


class MarketDataFetchError(Exception):
    pass


VALID_PERIODS = {
    "1d",
    "5d",
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "ytd",
    "max",
}

VALID_INTERVALS = {
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "60m",
    "90m",
    "1h",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo",
}


def _clean_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        float_value = float(value)
    except (TypeError, ValueError):
        return None

    if math.isnan(float_value):
        return None

    return float_value


def _clean_int(value: Any) -> int:
    if value is None:
        return 0

    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def fetch_quote(symbol: str) -> dict[str, Any]:
    normalized_symbol = symbol.upper().strip()

    if not normalized_symbol:
        raise MarketDataFetchError("Stock symbol is required.")

    ticker = yf.Ticker(normalized_symbol)

    try:
        info = ticker.info
    except Exception as exc:
        raise MarketDataFetchError("Unable to fetch quote data.") from exc

    if not info:
        raise MarketDataFetchError("No quote data found for this symbol.")

    current_price = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("previousClose")
    )

    return {
        "symbol": normalized_symbol,
        "current_price": _clean_float(current_price),
        "previous_close": _clean_float(info.get("previousClose")),
        "open_price": _clean_float(info.get("open")),
        "day_high": _clean_float(info.get("dayHigh")),
        "day_low": _clean_float(info.get("dayLow")),
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
    }


def fetch_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
) -> dict[str, Any]:
    normalized_symbol = symbol.upper().strip()

    if not normalized_symbol:
        raise MarketDataFetchError("Stock symbol is required.")

    if period not in VALID_PERIODS:
        raise MarketDataFetchError("Invalid period.")

    if interval not in VALID_INTERVALS:
        raise MarketDataFetchError("Invalid interval.")

    ticker = yf.Ticker(normalized_symbol)

    try:
        history_df = ticker.history(period=period, interval=interval)
    except Exception as exc:
        raise MarketDataFetchError("Unable to fetch historical data.") from exc

    if history_df.empty:
        raise MarketDataFetchError("No historical data found for this symbol.")

    prices = []

    for index, row in history_df.iterrows():
        open_price = _clean_float(row.get("Open"))
        high_price = _clean_float(row.get("High"))
        low_price = _clean_float(row.get("Low"))
        close_price = _clean_float(row.get("Close"))

        if (
            open_price is None
            or high_price is None
            or low_price is None
            or close_price is None
        ):
            continue

        date_value = index.strftime("%Y-%m-%d %H:%M:%S")

        prices.append(
            {
                "date": date_value,
                "open_price": open_price,
                "high_price": high_price,
                "low_price": low_price,
                "close_price": close_price,
                "volume": _clean_int(row.get("Volume")),
            }
        )

    if not prices:
        raise MarketDataFetchError("No valid historical price rows found.")

    return {
        "symbol": normalized_symbol,
        "period": period,
        "interval": interval,
        "prices": prices,
    }