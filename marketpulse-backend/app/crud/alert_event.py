from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.alert_event import AlertEvent


def create_alert_event(
    db: Session,
    alert_rule_id: int,
    stock_symbol: str,
    triggered_value: float,
    target_value: float,
    message: str,
) -> AlertEvent:
    alert_event = AlertEvent(
        alert_rule_id=alert_rule_id,
        stock_symbol=stock_symbol,
        triggered_value=triggered_value,
        target_value=target_value,
        message=message,
    )

    db.add(alert_event)
    db.commit()
    db.refresh(alert_event)

    return alert_event


def get_alert_event_by_id(
    db: Session,
    alert_event_id: int,
) -> AlertEvent | None:
    return db.query(AlertEvent).filter(AlertEvent.id == alert_event_id).first()


def get_alert_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[AlertEvent]:
    return db.query(AlertEvent).offset(skip).limit(limit).all()


def get_alert_events_by_rule_id(
    db: Session,
    alert_rule_id: int,
) -> list[AlertEvent]:
    return (
        db.query(AlertEvent)
        .filter(AlertEvent.alert_rule_id == alert_rule_id)
        .all()
    )


def get_latest_alert_event_by_rule_id(
    db: Session,
    alert_rule_id: int,
) -> AlertEvent | None:
    return (
        db.query(AlertEvent)
        .filter(AlertEvent.alert_rule_id == alert_rule_id)
        .order_by(AlertEvent.triggered_at.desc())
        .first()
    )


def has_recent_alert_event_for_rule(
    db: Session,
    alert_rule_id: int,
    cooldown_minutes: int,
) -> bool:
    cooldown_threshold = datetime.now(timezone.utc) - timedelta(
        minutes=cooldown_minutes
    )

    recent_alert_event = (
        db.query(AlertEvent)
        .filter(AlertEvent.alert_rule_id == alert_rule_id)
        .filter(AlertEvent.triggered_at >= cooldown_threshold)
        .first()
    )

    return recent_alert_event is not None