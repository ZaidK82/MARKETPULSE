from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StockCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    name: str | None = Field(default=None, max_length=255)
    exchange: str | None = Field(default=None, max_length=50)
    currency: str | None = Field(default=None, max_length=20)


class StockRead(BaseModel):
    id: int
    symbol: str
    name: str | None
    exchange: str | None
    currency: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)