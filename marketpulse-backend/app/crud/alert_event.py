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