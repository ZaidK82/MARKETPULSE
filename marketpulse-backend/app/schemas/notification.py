from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationLogRead(BaseModel):
    id: int
    alert_event_id: int
    channel: str
    status: str
    response_message: str | None
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationSendResultRead(BaseModel):
    alert_event_id: int
    channel: str
    status: str
    response_message: str | None
    notification_log_id: int