from typing import Callable

from sqlalchemy.orm import Session

from app.crud.alert_event import create_alert_event
from app.models.alert_rule import AlertRule
from app.models.stock import Stock
from app.services.indicator_service import (
    IndicatorCalculationError,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
)
from app.services.market_data_service import MarketDataFetchError, fetch_quote


class AlertEvaluationError(Exception):
    pass


def _compare_values(
    current_value: float,
    operator: str,
    target_value: float,
) -> bool:
    operators: dict[str, Callable[[float, float], bool]] = {
        ">": lambda current, target: current > target,
        ">=": lambda current, target: current >= target,
        "<": lambda current, target: current < target,
        "<=": lambda current, target: current <= target,
        "==": lambda current, target: current == target,
        "!=": lambda current, target: current != target,
    }

    if operator not in operators:
        raise AlertEvaluationError(f"Unsupported operator: {operator}")

    return operators[operator](current_value, target_value)


def _latest_indicator_value(indicator_response: dict, value_key: str = "value") -> float:
    values = indicator_response.get("values", [])

    if not values:
        raise AlertEvaluationError("No indicator values available.")

    for point in reversed(values):
        value = point.get(value_key)

        if value is not None:
            return float(value)

    raise AlertEvaluationError("No valid latest indicator value available.")


def _get_current_value(
    stock_symbol: str,
    indicator: str,
    timeframe: str,
) -> float:
    if indicator == "close_price":
        try:
            quote = fetch_quote(stock_symbol)
        except MarketDataFetchError as exc:
            raise AlertEvaluationError(str(exc)) from exc

        current_price = quote.get("current_price")

        if current_price is None:
            raise AlertEvaluationError("Current price unavailable.")

        return float(current_price)

    if indicator == "sma":
        try:
            response = calculate_sma(
                symbol=stock_symbol,
                window=20,
                period="6mo",
                interval=timeframe,
            )
        except IndicatorCalculationError as exc:
            raise AlertEvaluationError(str(exc)) from exc

        return _latest_indicator_value(response)

    if indicator == "ema":
        try:
            response = calculate_ema(
                symbol=stock_symbol,
                window=20,
                period="6mo",
                interval=timeframe,
            )
        except IndicatorCalculationError as exc:
            raise AlertEvaluationError(str(exc)) from exc

        return _latest_indicator_value(response)

    if indicator == "rsi":
        try:
            response = calculate_rsi(
                symbol=stock_symbol,
                window=14,
                period="6mo",
                interval=timeframe,
            )
        except IndicatorCalculationError as exc:
            raise AlertEvaluationError(str(exc)) from exc

        return _latest_indicator_value(response)

    if indicator in {"macd", "macd_signal", "macd_histogram"}:
        try:
            response = calculate_macd(
                symbol=stock_symbol,
                fast_window=12,
                slow_window=26,
                signal_window=9,
                period="6mo",
                interval=timeframe,
            )
        except IndicatorCalculationError as exc:
            raise AlertEvaluationError(str(exc)) from exc

        value_key_map = {
            "macd": "macd",
            "macd_signal": "signal",
            "macd_histogram": "histogram",
        }

        return _latest_indicator_value(
            response,
            value_key=value_key_map[indicator],
        )

    raise AlertEvaluationError(f"Unsupported indicator: {indicator}")


def evaluate_alert_rule(
    db: Session,
    alert_rule: AlertRule,
    stock: Stock,
) -> dict:
    if not alert_rule.is_active:
        raise AlertEvaluationError("Alert rule is inactive.")

    current_value = _get_current_value(
        stock_symbol=stock.symbol,
        indicator=alert_rule.indicator,
        timeframe=alert_rule.timeframe,
    )

    triggered = _compare_values(
        current_value=current_value,
        operator=alert_rule.operator,
        target_value=alert_rule.target_value,
    )

    message = (
        f"{stock.symbol} {alert_rule.indicator} is {current_value} "
        f"and rule is {alert_rule.indicator} {alert_rule.operator} "
        f"{alert_rule.target_value}. Triggered: {triggered}."
    )

    alert_event_id = None

    if triggered:
        alert_event = create_alert_event(
            db=db,
            alert_rule_id=alert_rule.id,
            stock_symbol=stock.symbol,
            triggered_value=current_value,
            target_value=alert_rule.target_value,
            message=message,
        )

        alert_event_id = alert_event.id

    return {
        "rule_id": alert_rule.id,
        "stock_id": stock.id,
        "stock_symbol": stock.symbol,
        "indicator": alert_rule.indicator,
        "operator": alert_rule.operator,
        "target_value": alert_rule.target_value,
        "current_value": current_value,
        "triggered": triggered,
        "message": message,
        "alert_event_id": alert_event_id,
    }