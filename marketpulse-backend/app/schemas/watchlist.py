from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.stock import StockRead


class WatchlistItemCreate(BaseModel):
    stock_id: int


class WatchlistItemRead(BaseModel):
    id: int
    stock_id: int
    is_active: bool
    created_at: datetime
    stock: StockRead

    model_config = ConfigDict(from_attributes=True)