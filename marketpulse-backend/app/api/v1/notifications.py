from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.alert_event import get_alert_events
from app.crud.notification_log import get_notification_logs
from app.models.alert_event import AlertEvent
from app.schemas.evaluation import AlertEventRead
from app.schemas.notification import NotificationLogRead, NotificationSendResultRead
from app.services.notification_service import NotificationError, send_discord_notification


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def get_alert_event_by_id(db: Session, alert_event_id: int) -> AlertEvent | None:
    return db.query(AlertEvent).filter(AlertEvent.id == alert_event_id).first()


@router.post(
    "/alert-events/{alert_event_id}/discord",
    response_model=NotificationSendResultRead,
)
def send_discord_notification_endpoint(
    alert_event_id: int,
    db: Session = Depends(get_db),
):
    alert_event = get_alert_event_by_id(db, alert_event_id)

    if not alert_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert event not found.",
        )

    try:
        return send_discord_notification(
            db=db,
            alert_event=alert_event,
        )
    except NotificationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/logs",
    response_model=list[NotificationLogRead],
)
def list_notification_logs_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_notification_logs(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/alert-events",
    response_model=list[AlertEventRead],
)
def list_alert_events_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_alert_events(
        db=db,
        skip=skip,
        limit=limit,
    )