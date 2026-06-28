from sqlalchemy.orm import Session

from app.config import settings
from app.crud.alert_rule import get_alert_rules
from app.crud.stock import get_stock_by_id
from app.models.alert_rule import AlertRule
from app.services.evaluation_service import AlertEvaluationError, evaluate_alert_rule
from app.services.notification_service import NotificationError, send_discord_notification
from app.models.alert_event import AlertEvent


def _get_alert_event_by_id(db: Session, alert_event_id: int) -> AlertEvent | None:
    return db.query(AlertEvent).filter(AlertEvent.id == alert_event_id).first()


def run_alert_evaluation_job(db: Session) -> dict:
    active_rules: list[AlertRule] = get_alert_rules(
        db=db,
        skip=0,
        limit=1000,
        active_only=True,
    )

    evaluated_rules = 0
    triggered_rules = 0
    notifications_attempted = 0
    notifications_sent = 0
    errors: list[str] = []

    for rule in active_rules:
        evaluated_rules += 1

        stock = get_stock_by_id(db, rule.stock_id)

        if not stock:
            errors.append(
                f"Rule {rule.id}: stock_id {rule.stock_id} not found."
            )
            continue

        try:
            evaluation_result = evaluate_alert_rule(
                db=db,
                alert_rule=rule,
                stock=stock,
            )
        except AlertEvaluationError as exc:
            errors.append(f"Rule {rule.id}: evaluation failed: {exc}")
            continue

        if not evaluation_result["triggered"]:
            continue

        triggered_rules += 1

        alert_event_id = evaluation_result.get("alert_event_id")

        if alert_event_id is None:
            errors.append(f"Rule {rule.id}: triggered but no alert event was created.")
            continue

        alert_event = _get_alert_event_by_id(
            db=db,
            alert_event_id=alert_event_id,
        )

        if not alert_event:
            errors.append(f"Rule {rule.id}: alert event {alert_event_id} not found.")
            continue

        notifications_attempted += 1

        try:
            send_result = send_discord_notification(
                db=db,
                alert_event=alert_event,
            )

            if send_result["status"] == "sent":
                notifications_sent += 1

        except NotificationError as exc:
            errors.append(f"Rule {rule.id}: notification failed: {exc}")
        except Exception as exc:
            errors.append(f"Rule {rule.id}: unexpected notification error: {exc}")

    return {
        "evaluated_rules": evaluated_rules,
        "triggered_rules": triggered_rules,
        "notifications_attempted": notifications_attempted,
        "notifications_sent": notifications_sent,
        "errors": errors,
    }


def get_scheduler_status() -> dict:
    mode = "background-enabled" if settings.SCHEDULER_ENABLED else "manual-run-once"

    return {
        "scheduler_enabled": settings.SCHEDULER_ENABLED,
        "interval_minutes": settings.SCHEDULER_INTERVAL_MINUTES,
        "mode": mode,
    }