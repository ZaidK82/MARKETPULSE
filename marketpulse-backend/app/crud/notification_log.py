from sqlalchemy.orm import Session

from app.models.notification_log import NotificationLog


def create_notification_log(
    db: Session,
    alert_event_id: int,
    channel: str,
    status: str,
    response_message: str | None = None,
) -> NotificationLog:
    notification_log = NotificationLog(
        alert_event_id=alert_event_id,
        channel=channel,
        status=status,
        response_message=response_message,
    )

    db.add(notification_log)
    db.commit()
    db.refresh(notification_log)

    return notification_log


def get_notification_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[NotificationLog]:
    return db.query(NotificationLog).offset(skip).limit(limit).all()


def get_notification_logs_by_alert_event_id(
    db: Session,
    alert_event_id: int,
) -> list[NotificationLog]:
    return (
        db.query(NotificationLog)
        .filter(NotificationLog.alert_event_id == alert_event_id)
        .all()
    )