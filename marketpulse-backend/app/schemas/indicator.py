from pydantic import BaseModel


class IndicatorPointRead(BaseModel):
    date: str
    value: float | None


class IndicatorSeriesRead(BaseModel):
    symbol: str
    indicator: str
    period: str
    interval: str
    window: int
    values: list[IndicatorPointRead]


class MACDPointRead(BaseModel):
    date: str
    macd: float | None
    signal: float | None
    histogram: float | None


class MACDSeriesRead(BaseModel):
    symbol: str
    indicator: str
    period: str
    interval: str
    fast_window: int
    slow_window: int
    signal_window: int
    values: list[MACDPointRead]