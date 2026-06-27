from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import settings
from app.core.init_db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="MarketPulse Stock Alert System Backend API",
        lifespan=lifespan,
    )

    app.include_router(
        api_router,
        prefix=settings.API_V1_PREFIX,
    )

    return app


app = create_app()