from pydantic import BaseModel


class SchedulerRunResultRead(BaseModel):
    evaluated_rules: int
    triggered_rules: int
    notifications_attempted: int
    notifications_sent: int
    errors: list[str]


class SchedulerStatusRead(BaseModel):
    scheduler_enabled: bool
    interval_minutes: int
    mode: str