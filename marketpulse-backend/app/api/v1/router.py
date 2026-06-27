from fastapi import APIRouter

from app.api.v1 import (
    alert_rules,
    evaluation,
    health,
    indicators,
    market_data,
    stocks,
    watchlist,
)


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(stocks.router)
api_router.include_router(watchlist.router)
api_router.include_router(market_data.router)
api_router.include_router(indicators.router)
api_router.include_router(alert_rules.router)
api_router.include_router(evaluation.router)