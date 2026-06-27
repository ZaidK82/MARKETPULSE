from typing import Any

import pandas as pd

from app.services.market_data_service import MarketDataFetchError, fetch_history


class IndicatorCalculationError(Exception):
    pass


def _historical_prices_to_dataframe(history: dict[str, Any]) -> pd.DataFrame:
    prices = history.get("prices", [])

    if not prices:
        raise IndicatorCalculationError("No historical prices available.")

    df = pd.DataFrame(prices)

    required_columns = {"date", "close_price"}

    if not required_columns.issubset(df.columns):
        raise IndicatorCalculationError("Historical prices are missing required columns.")

    df["close_price"] = pd.to_numeric(df["close_price"], errors="coerce")
    df = df.dropna(subset=["close_price"])

    if df.empty:
        raise IndicatorCalculationError("No valid closing prices available.")

    return df


def _clean_indicator_value(value: Any) -> float | None:
    if pd.isna(value):
        return None

    return round(float(value), 4)


def calculate_sma(
    symbol: str,
    window: int = 20,
    period: str = "6mo",
    interval: str = "1d",
) -> dict[str, Any]:
    if window <= 0:
        raise IndicatorCalculationError("Window must be greater than zero.")

    try:
        history = fetch_history(symbol=symbol, period=period, interval=interval)
    except MarketDataFetchError as exc:
        raise IndicatorCalculationError(str(exc)) from exc

    df = _historical_prices_to_dataframe(history)

    df["sma"] = df["close_price"].rolling(window=window).mean()

    values = [
        {
            "date": row["date"],
            "value": _clean_indicator_value(row["sma"]),
        }
        for _, row in df.iterrows()
    ]

    return {
        "symbol": history["symbol"],
        "indicator": "SMA",
        "period": period,
        "interval": interval,
        "window": window,
        "values": values,
    }


def calculate_ema(
    symbol: str,
    window: int = 20,
    period: str = "6mo",
    interval: str = "1d",
) -> dict[str, Any]:
    if window <= 0:
        raise IndicatorCalculationError("Window must be greater than zero.")

    try:
        history = fetch_history(symbol=symbol, period=period, interval=interval)
    except MarketDataFetchError as exc:
        raise IndicatorCalculationError(str(exc)) from exc

    df = _historical_prices_to_dataframe(history)

    df["ema"] = df["close_price"].ewm(span=window, adjust=False).mean()

    values = [
        {
            "date": row["date"],
            "value": _clean_indicator_value(row["ema"]),
        }
        for _, row in df.iterrows()
    ]

    return {
        "symbol": history["symbol"],
        "indicator": "EMA",
        "period": period,
        "interval": interval,
        "window": window,
        "values": values,
    }


def calculate_rsi(
    symbol: str,
    window: int = 14,
    period: str = "6mo",
    interval: str = "1d",
) -> dict[str, Any]:
    if window <= 0:
        raise IndicatorCalculationError("Window must be greater than zero.")

    try:
        history = fetch_history(symbol=symbol, period=period, interval=interval)
    except MarketDataFetchError as exc:
        raise IndicatorCalculationError(str(exc)) from exc

    df = _historical_prices_to_dataframe(history)

    delta = df["close_price"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.rolling(window=window).mean()
    average_loss = loss.rolling(window=window).mean()

    relative_strength = average_gain / average_loss
    rsi = 100 - (100 / (1 + relative_strength))

    df["rsi"] = rsi

    values = [
        {
            "date": row["date"],
            "value": _clean_indicator_value(row["rsi"]),
        }
        for _, row in df.iterrows()
    ]

    return {
        "symbol": history["symbol"],
        "indicator": "RSI",
        "period": period,
        "interval": interval,
        "window": window,
        "values": values,
    }


def calculate_macd(
    symbol: str,
    fast_window: int = 12,
    slow_window: int = 26,
    signal_window: int = 9,
    period: str = "6mo",
    interval: str = "1d",
) -> dict[str, Any]:
    if fast_window <= 0 or slow_window <= 0 or signal_window <= 0:
        raise IndicatorCalculationError("MACD windows must be greater than zero.")

    if fast_window >= slow_window:
        raise IndicatorCalculationError("Fast window must be smaller than slow window.")

    try:
        history = fetch_history(symbol=symbol, period=period, interval=interval)
    except MarketDataFetchError as exc:
        raise IndicatorCalculationError(str(exc)) from exc

    df = _historical_prices_to_dataframe(history)

    fast_ema = df["close_price"].ewm(span=fast_window, adjust=False).mean()
    slow_ema = df["close_price"].ewm(span=slow_window, adjust=False).mean()

    df["macd"] = fast_ema - slow_ema
    df["signal"] = df["macd"].ewm(span=signal_window, adjust=False).mean()
    df["histogram"] = df["macd"] - df["signal"]

    values = [
        {
            "date": row["date"],
            "macd": _clean_indicator_value(row["macd"]),
            "signal": _clean_indicator_value(row["signal"]),
            "histogram": _clean_indicator_value(row["histogram"]),
        }
        for _, row in df.iterrows()
    ]

    return {
        "symbol": history["symbol"],
        "indicator": "MACD",
        "period": period,
        "interval": interval,
        "fast_window": fast_window,
        "slow_window": slow_window,
        "signal_window": signal_window,
        "values": values,
    }