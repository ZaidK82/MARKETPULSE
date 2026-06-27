from fastapi import APIRouter

from app.api.v1 import health, stocks, watchlist


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(stocks.router)
api_router.include_router(watchlist.router)