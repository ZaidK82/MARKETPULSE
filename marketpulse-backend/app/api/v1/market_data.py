from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.market_data import HistoricalDataRead, QuoteRead
from app.services.market_data_service import (
    MarketDataFetchError,
    fetch_history,
    fetch_quote,
)


router = APIRouter(
    prefix="/market-data",
    tags=["Market Data"],
)


@router.get(
    "/{symbol}/quote",
    response_model=QuoteRead,
)
def get_quote_endpoint(symbol: str):
    try:
        return fetch_quote(symbol)
    except MarketDataFetchError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{symbol}/history",
    response_model=HistoricalDataRead,
)
def get_history_endpoint(
    symbol: str,
    period: str = Query(default="1mo"),
    interval: str = Query(default="1d"),
):
    try:
        return fetch_history(
            symbol=symbol,
            period=period,
            interval=interval,
        )
    except MarketDataFetchError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc