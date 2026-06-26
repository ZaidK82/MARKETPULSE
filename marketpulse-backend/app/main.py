from fastapi import FastAPI

from app.config import settings
from app.api.v1.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="MarketPulse Stock Alert System Backend API",
    )

    app.include_router(
        api_router,
        prefix=settings.API_V1_PREFIX,
    )

    return app


app = create_app()