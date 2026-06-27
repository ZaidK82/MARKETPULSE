from pydantic import BaseModel, Field


class QuoteRead(BaseModel):
    symbol: str
    current_price: float | None = None
    previous_close: float | None = None
    open_price: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    currency: str | None = None
    exchange: str | None = None


class HistoricalPriceRead(BaseModel):
    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int


class HistoricalDataRead(BaseModel):
    symbol: str
    period: str
    interval: str
    prices: list[HistoricalPriceRead]


class MarketDataError(BaseModel):
    detail: str = Field(..., examples=["Unable to fetch market data."])