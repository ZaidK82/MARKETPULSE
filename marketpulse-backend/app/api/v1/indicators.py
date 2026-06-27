from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.indicator import IndicatorSeriesRead, MACDSeriesRead
from app.services.indicator_service import (
    IndicatorCalculationError,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
)


router = APIRouter(
    prefix="/indicators",
    tags=["Indicators"],
)


@router.get(
    "/{symbol}/sma",
    response_model=IndicatorSeriesRead,
)
def get_sma_endpoint(
    symbol: str,
    window: int = Query(default=20, ge=1),
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
):
    try:
        return calculate_sma(
            symbol=symbol,
            window=window,
            period=period,
            interval=interval,
        )
    except IndicatorCalculationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{symbol}/ema",
    response_model=IndicatorSeriesRead,
)
def get_ema_endpoint(
    symbol: str,
    window: int = Query(default=20, ge=1),
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
):
    try:
        return calculate_ema(
            symbol=symbol,
            window=window,
            period=period,
            interval=interval,
        )
    except IndicatorCalculationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{symbol}/rsi",
    response_model=IndicatorSeriesRead,
)
def get_rsi_endpoint(
    symbol: str,
    window: int = Query(default=14, ge=1),
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
):
    try:
        return calculate_rsi(
            symbol=symbol,
            window=window,
            period=period,
            interval=interval,
        )
    except IndicatorCalculationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{symbol}/macd",
    response_model=MACDSeriesRead,
)
def get_macd_endpoint(
    symbol: str,
    fast_window: int = Query(default=12, ge=1),
    slow_window: int = Query(default=26, ge=1),
    signal_window: int = Query(default=9, ge=1),
    period: str = Query(default="6mo"),
    interval: str = Query(default="1d"),
):
    try:
        return calculate_macd(
            symbol=symbol,
            fast_window=fast_window,
            slow_window=slow_window,
            signal_window=signal_window,
            period=period,
            interval=interval,
        )
    except IndicatorCalculationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc