from datetime import datetime

from pydantic import BaseModel


class EvaluationResultRead(BaseModel):
    rule_id: int
    stock_id: int
    stock_symbol: str
    indicator: str
    operator: str
    target_value: float
    current_value: float
    triggered: bool
    message: str
    alert_event_id: int | None = None


class AlertEventRead(BaseModel):
    id: int
    alert_rule_id: int
    stock_symbol: str
    triggered_value: float
    target_value: float
    message: str
    triggered_at: datetime