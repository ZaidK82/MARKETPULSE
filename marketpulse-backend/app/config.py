from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "MarketPulse"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"

    DATABASE_URL: str = "sqlite:///./marketpulse.db"

    API_V1_PREFIX: str = "/api/v1"

    DISCORD_WEBHOOK_URL: str | None = None

    SCHEDULER_ENABLED: bool = False
    SCHEDULER_INTERVAL_MINUTES: int = 15

    CRON_SECRET: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()