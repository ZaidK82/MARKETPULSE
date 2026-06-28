import requests
from sqlalchemy.orm import Session

from app.config import settings
from app.crud.notification_log import create_notification_log
from app.models.alert_event import AlertEvent


class NotificationError(Exception):
    pass


def build_discord_alert_message(alert_event: AlertEvent) -> str:
    return (
        "🚨 **MarketPulse Alert Triggered**\n\n"
        f"**Stock:** {alert_event.stock_symbol}\n"
        f"**Triggered Value:** {alert_event.triggered_value}\n"
        f"**Target Value:** {alert_event.target_value}\n"
        f"**Message:** {alert_event.message}\n"
        f"**Triggered At:** {alert_event.triggered_at}"
    )


def send_discord_notification(
    db: Session,
    alert_event: AlertEvent,
    webhook_url: str | None = None,
) -> dict:
    final_webhook_url = webhook_url or settings.DISCORD_WEBHOOK_URL

    if not final_webhook_url:
        notification_log = create_notification_log(
            db=db,
            alert_event_id=alert_event.id,
            channel="discord",
            status="failed",
            response_message="Discord webhook URL is not configured.",
        )

        raise NotificationError(
            f"Discord webhook URL is not configured. "
            f"Notification log ID: {notification_log.id}"
        )

    message = build_discord_alert_message(alert_event)

    payload = {
        "content": message,
    }

    try:
        response = requests.post(
            final_webhook_url,
            json=payload,
            timeout=10,
        )
    except requests.RequestException as exc:
        notification_log = create_notification_log(
            db=db,
            alert_event_id=alert_event.id,
            channel="discord",
            status="failed",
            response_message=str(exc),
        )

        raise NotificationError(
            f"Discord notification request failed. "
            f"Notification log ID: {notification_log.id}"
        ) from exc

    if response.status_code not in {200, 204}:
        notification_log = create_notification_log(
            db=db,
            alert_event_id=alert_event.id,
            channel="discord",
            status="failed",
            response_message=f"Discord returned status code {response.status_code}.",
        )

        raise NotificationError(
            f"Discord notification failed. "
            f"Notification log ID: {notification_log.id}"
        )

    notification_log = create_notification_log(
        db=db,
        alert_event_id=alert_event.id,
        channel="discord",
        status="sent",
        response_message="Discord notification sent successfully.",
    )

    return {
        "alert_event_id": alert_event.id,
        "channel": "discord",
        "status": "sent",
        "response_message": "Discord notification sent successfully.",
        "notification_log_id": notification_log.id,
    }