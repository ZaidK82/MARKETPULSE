from fastapi import APIRouter

from app.api.v1 import health, market_data, stocks, watchlist


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(stocks.router)
api_router.include_router(watchlist.router)
api_router.include_router(market_data.router)